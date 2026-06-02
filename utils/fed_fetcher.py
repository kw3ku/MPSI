"""
Fetch new Fed documents from the Federal Reserve website.
"""

import re
from typing import Optional
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path


class FedDocumentFetcher:
    """Download and persist Federal Reserve press releases."""

    FOMC_STATEMENTS_URL = "https://www.federalreserve.gov/newsevents/pressreleases.htm"
    BASE_URL            = "https://www.federalreserve.gov"

    _HEADERS = {'User-Agent': 'Mozilla/5.0 (academic research)'}

    def get_latest_statement(self) -> list[dict]:
        """Return metadata for the five most recent FOMC monetary-policy releases."""
        try:
            resp = requests.get(
                self.FOMC_STATEMENTS_URL, headers=self._HEADERS, timeout=10
            )
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')

            links = soup.find_all('a', href=re.compile(r'monetary.*\.htm'))
            results = []
            for link in links[:5]:
                href = link.get('href', '')
                if not href.startswith('http'):
                    href = self.BASE_URL + href
                date_match = re.search(r'(\d{8})', href)
                results.append({
                    'url':   href,
                    'title': link.get_text(strip=True),
                    'date':  date_match.group(1) if date_match else 'unknown',
                })
            return results

        except Exception as exc:
            print(f"[FedFetcher] fetch error: {exc}")
            return []

    def fetch_and_save(
        self,
        url: str,
        save_dir: str = "data/us_fed/fomc_statements",
    ) -> tuple[Optional[str], Optional[str]]:
        """Download a statement page, save its text, return (path, text)."""
        try:
            resp = requests.get(url, headers=self._HEADERS, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')

            content_div = (
                soup.find('div', class_='col-xs-12')
                or soup.find('div', id='article')
                or soup.find('article')
                or soup.find('div', class_='renderedcontent')
            )
            text = (
                content_div.get_text(separator='\n', strip=True)
                if content_div
                else soup.get_text()
            )

            date_match = re.search(r'(\d{8})', url)
            date_str   = date_match.group(1) if date_match else datetime.now().strftime('%Y%m%d')
            filename   = f"fomc_st_{date_str}.txt"

            save_path = Path(save_dir) / filename
            save_path.parent.mkdir(parents=True, exist_ok=True)
            save_path.write_text(text, encoding='utf-8')

            print(f"[FedFetcher] saved {filename} ({len(text.split())} words)")
            return str(save_path), text

        except Exception as exc:
            print(f"[FedFetcher] download error: {exc}")
            return None, None
