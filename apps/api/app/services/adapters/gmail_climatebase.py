from __future__ import annotations

import base64
import binascii
import html
import os
import re
from datetime import datetime, timezone
from email import message_from_bytes
from email.message import Message
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse

import httpx

from app.services.adapters.base import FetchCursor, NormalizedJob, RawJobDetail, RawListing, SourceAdapter, SourceRegistryEntry

GMAIL_API_BASE = "https://gmail.googleapis.com/gmail/v1/users/me"
CLIMATEBASE_HOSTS = {"climatebase.org", "www.climatebase.org"}
DEFAULT_GMAIL_QUERY = 'from:(climatebase.org) newer_than:30d'
DEFAULT_MAX_MESSAGES = 20
DEFAULT_PROCESSED_WINDOW = 200
URL_RE = re.compile(r"https?://[^\s<>'\")]+")
HTML_LINK_RE = re.compile(r'href=["\']([^"\']+)["\']', re.IGNORECASE)


class GmailClimatebaseAdapter(SourceAdapter):
    slug = "gmail_climatebase"

    def __init__(self, client: httpx.Client | None = None) -> None:
        self.client = client or httpx.Client(timeout=30, follow_redirects=True)

    def fetch_listings(
        self,
        registry: SourceRegistryEntry,
        cursor: FetchCursor,
    ) -> tuple[list[RawListing], FetchCursor]:
        query = (registry.config or {}).get("gmail_query") or DEFAULT_GMAIL_QUERY
        max_messages = int((registry.config or {}).get("max_messages", DEFAULT_MAX_MESSAGES))
        processed_window = int((registry.config or {}).get("processed_message_window", DEFAULT_PROCESSED_WINDOW))
        token = _gmail_access_token(registry.config or {})

        processed_ids = list((cursor.state or {}).get("processed_message_ids") or [])
        processed_set = set(processed_ids)

        message_refs = self._list_messages(token, query=query, max_results=max_messages)
        now = datetime.now(timezone.utc)
        listings: list[RawListing] = []
        seen_urls: set[str] = set()
        newly_processed_ids: list[str] = []

        for ref in message_refs:
            message_id = ref.get("id")
            if not message_id or message_id in processed_set:
                continue

            message = self._get_message(token, message_id)
            extracted = _extract_climatebase_links_from_gmail_message(message)
            newly_processed_ids.append(message_id)

            for candidate in extracted["links"]:
                url = candidate["url"]
                dedupe_key = url
                if dedupe_key in seen_urls:
                    continue
                seen_urls.add(dedupe_key)
                listings.append(
                    RawListing(
                        source_slug=self.slug,
                        discovered_at=now,
                        url=url,
                        external_id=candidate.get("external_id"),
                        title_hint=candidate.get("title_hint"),
                        company_hint=candidate.get("company_hint"),
                        location_hint=candidate.get("location_hint"),
                        raw_payload={
                            "job": candidate.get("job"),
                            "target_adapter": "climatebase_v1",
                            "target_source_slug": "climatebase",
                            "gmail_provenance": {
                                "message_id": message_id,
                                "thread_id": message.get("threadId"),
                                "history_id": message.get("historyId"),
                                "internal_date": message.get("internalDate"),
                                "subject": extracted.get("subject"),
                                "from": extracted.get("from"),
                                "matched_query": query,
                            },
                        },
                    )
                )

        updated_ids = (newly_processed_ids + processed_ids)[:processed_window]
        next_state = dict(cursor.state or {})
        next_state.update(
            {
                "processed_message_ids": updated_ids,
                "last_query": query,
                "last_message_count": len(message_refs),
                "last_processed_at": now.isoformat(),
            }
        )
        return listings, FetchCursor(next_state)

    def fetch_job_detail(self, listing: RawListing, registry: SourceRegistryEntry) -> RawJobDetail:
        raise NotImplementedError("gmail_climatebase is discovery-only; detail fetch should route to climatebase_v1")

    def normalize(self, detail: RawJobDetail, listing: RawListing | None = None) -> NormalizedJob:
        raise NotImplementedError("gmail_climatebase is discovery-only; normalization should route to climatebase_v1")

    def _list_messages(self, access_token: str, query: str, max_results: int) -> list[dict[str, Any]]:
        resp = self.client.get(
            f"{GMAIL_API_BASE}/messages",
            headers=_gmail_headers(access_token),
            params={"q": query, "maxResults": max_results},
        )
        resp.raise_for_status()
        payload = resp.json()
        messages = payload.get("messages") or []
        return [item for item in messages if isinstance(item, dict)]

    def _get_message(self, access_token: str, message_id: str) -> dict[str, Any]:
        resp = self.client.get(
            f"{GMAIL_API_BASE}/messages/{message_id}",
            headers=_gmail_headers(access_token),
            params={"format": "raw"},
        )
        resp.raise_for_status()
        return resp.json()


def _gmail_headers(access_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {access_token}"}


def _gmail_access_token(config: dict[str, Any]) -> str:
    env_name = config.get("gmail_access_token_env") or "GMAIL_ACCESS_TOKEN"
    token = os.getenv(env_name, "").strip()
    if token:
        return token
    raise RuntimeError(f"Missing Gmail access token in env var {env_name}")


def _extract_climatebase_links_from_gmail_message(message: dict[str, Any]) -> dict[str, Any]:
    raw_value = message.get("raw")
    if not raw_value:
        raise ValueError("Gmail message did not include raw payload")

    email_message = message_from_bytes(_urlsafe_b64decode(raw_value))
    subject = _header_value(email_message, "Subject")
    from_value = _header_value(email_message, "From")

    html_parts = _collect_body_parts(email_message, preferred_content_type="text/html")
    text_parts = _collect_body_parts(email_message, preferred_content_type="text/plain")

    links: list[dict[str, Any]] = []
    seen_urls: set[str] = set()
    for blob, is_html in [*[(part, True) for part in html_parts], *[(part, False) for part in text_parts]]:
        for candidate in _extract_candidate_links(blob, is_html=is_html):
            normalized = _normalize_climatebase_url(candidate)
            if not normalized or normalized in seen_urls:
                continue
            seen_urls.add(normalized)
            links.append(
                {
                    "url": normalized,
                    "external_id": _climatebase_external_id(normalized),
                    "title_hint": None,
                    "company_hint": None,
                    "location_hint": None,
                    "job": None,
                }
            )

    return {"subject": subject, "from": from_value, "links": links}


def _collect_body_parts(email_message: Message, preferred_content_type: str) -> list[str]:
    parts: list[str] = []
    if email_message.is_multipart():
        for part in email_message.walk():
            if part.get_content_type() != preferred_content_type:
                continue
            payload = part.get_payload(decode=True)
            if payload is None:
                continue
            charset = part.get_content_charset() or "utf-8"
            parts.append(payload.decode(charset, errors="ignore"))
    else:
        if email_message.get_content_type() == preferred_content_type:
            payload = email_message.get_payload(decode=True)
            if payload is not None:
                charset = email_message.get_content_charset() or "utf-8"
                parts.append(payload.decode(charset, errors="ignore"))
    return parts


def _extract_candidate_links(body: str, *, is_html: bool) -> list[str]:
    body = html.unescape(body or "")
    candidates: list[str] = []
    if is_html:
        candidates.extend(match.group(1) for match in HTML_LINK_RE.finditer(body))
    candidates.extend(URL_RE.findall(body))
    return candidates


def _normalize_climatebase_url(url: str) -> str | None:
    if not url:
        return None
    stripped = url.strip()
    parsed = urlparse(stripped)
    if not parsed.scheme or not parsed.netloc:
        return None

    host = parsed.netloc.lower()
    candidate = stripped

    if "mail.google.com" in host and parsed.path.endswith("/u/0/"):
        return None

    if host not in CLIMATEBASE_HOSTS:
        redirect_target = _extract_redirect_target(parsed)
        if not redirect_target:
            return None
        parsed = urlparse(redirect_target)
        if parsed.netloc.lower() not in CLIMATEBASE_HOSTS:
            return None
        candidate = redirect_target

    clean = parsed._replace(query="", fragment="")
    normalized = clean.geturl().rstrip("/")
    if "/jobs" not in parsed.path:
        return None
    return normalized


def _extract_redirect_target(parsed) -> str | None:
    query = parse_qs(parsed.query)
    for key in ("q", "url", "u", "redirect", "redirect_uri"):
        values = query.get(key) or []
        for value in values:
            decoded = unquote(value)
            if decoded.startswith("http://") or decoded.startswith("https://"):
                return decoded
    return None


def _climatebase_external_id(url: str) -> str | None:
    parsed = urlparse(url)
    chunks = [chunk for chunk in parsed.path.split("/") if chunk]
    if not chunks:
        return None
    last = chunks[-1]
    if last.isdigit():
        return last
    match = re.search(r"(\d+)$", last)
    if match:
        return match.group(1)
    return None


def _header_value(message: Message, header_name: str) -> str | None:
    value = message.get(header_name)
    return value.strip() if isinstance(value, str) and value.strip() else None


def _urlsafe_b64decode(value: str) -> bytes:
    padding = (-len(value)) % 4
    value += "=" * padding
    try:
        return base64.urlsafe_b64decode(value.encode("ascii"))
    except (ValueError, binascii.Error) as exc:
        raise ValueError("Invalid Gmail raw payload") from exc
