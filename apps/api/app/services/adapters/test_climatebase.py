from __future__ import annotations

import unittest

from app.services.adapters.climatebase import (
    _build_listing_url,
    _build_search_url,
    _compensation_text,
    _extract_jobs_from_next_data,
)


class ClimatebaseAdapterHelpersTest(unittest.TestCase):
    def test_extract_jobs_from_next_data(self) -> None:
        html = """
        <html>
          <body>
            <script id="__NEXT_DATA__" type="application/json">
              {"props":{"pageProps":{"jobs":[{"id":123,"title":"Climate PM","name_of_employer":"Sun Co"}]}}}
            </script>
          </body>
        </html>
        """

        jobs = _extract_jobs_from_next_data(html)

        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["id"], 123)
        self.assertEqual(jobs[0]["title"], "Climate PM")

    def test_build_search_url_includes_expected_filters(self) -> None:
        url = _build_search_url({"keywords": "technical product manager climate", "location": "Los Angeles, CA", "remote": True})

        self.assertEqual(
            url,
            "https://climatebase.org/jobs?query=technical+product+manager+climate&location=Los+Angeles%2C+CA&remote=true",
        )

    def test_build_listing_url_uses_stable_fragment_identifier(self) -> None:
        self.assertEqual(_build_listing_url(71427221), "https://climatebase.org/jobs#job-71427221")

    def test_compensation_text_normalizes_negative_prefixes(self) -> None:
        text = _compensation_text({"salary_from": "-127000", "salary_to": "158000", "salary_period": "yearly"})

        self.assertEqual(text, "Compensation: $127,000 - $158,000 per year")


if __name__ == "__main__":
    unittest.main()
