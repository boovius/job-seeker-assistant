from __future__ import annotations

import base64
import unittest
from email.message import EmailMessage

from app.services.adapters.gmail_climatebase import _extract_climatebase_links_from_gmail_message, _normalize_climatebase_url


class GmailClimatebaseHelpersTest(unittest.TestCase):
    def test_extracts_climatebase_links_from_html_and_redirects(self) -> None:
        email = EmailMessage()
        email["Subject"] = "Your Climatebase matches"
        email["From"] = "Climatebase <hello@climatebase.org>"
        email.set_content("Plain text fallback https://climatebase.org/jobs/789")
        email.add_alternative(
            """
            <html>
              <body>
                <a href="https://www.google.com/url?q=https%3A%2F%2Fclimatebase.org%2Fjobs%2F123%3Futm_source%3Demail">Job one</a>
                <a href="https://climatebase.org/jobs/456?utm_medium=email">Job two</a>
              </body>
            </html>
            """,
            subtype="html",
        )

        raw = base64.urlsafe_b64encode(email.as_bytes()).decode("ascii")
        message = {"raw": raw, "threadId": "thread-1", "historyId": "99"}

        extracted = _extract_climatebase_links_from_gmail_message(message)

        self.assertEqual(extracted["subject"], "Your Climatebase matches")
        self.assertEqual(
            [link["url"] for link in extracted["links"]],
            [
                "https://climatebase.org/jobs/123",
                "https://climatebase.org/jobs/456",
                "https://climatebase.org/jobs/789",
            ],
        )
        self.assertEqual([link["external_id"] for link in extracted["links"]], ["123", "456", "789"])

    def test_normalize_climatebase_url_rejects_non_climatebase_links(self) -> None:
        self.assertIsNone(_normalize_climatebase_url("https://example.com/jobs/123"))
        self.assertIsNone(_normalize_climatebase_url("mailto:test@example.com"))


if __name__ == "__main__":
    unittest.main()
