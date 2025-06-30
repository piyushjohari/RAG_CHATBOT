import requests
import time
import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import Set, List, Dict

class AngelOneFAQCrawler:
    """
    Crawler for the Angel One FAQ/Support static website.
    Scrapes categories, questions, answers into structured JSON.
    """
    BASE_URL = "https://www.angelone.in"
    START_PATH = "/support"
    DEFAULT_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/114.0.5735.133 Safari/537.36"
        )
    }

    def __init__(
        self,
        start_url: str = None,
        max_depth: int = 10,
        sleep_between_requests: float = 1.5
    ):
        """
        :param start_url: URL to begin crawling (defaults to Angel One support)
        :param max_depth: Maximum crawl depth
        :param sleep_between_requests: Politeness delay (seconds)
        """
        self.start_url = start_url or urljoin(self.BASE_URL, self.START_PATH)
        self.max_depth = max_depth
        self.sleep_between_requests = sleep_between_requests

        self.visited: Set[str] = set()
        self.faq_data: List[Dict[str, str]] = []
        logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    def crawl(self):
        """
        Start crawling from the initial URL, recursively.
        """
        logging.info(f"Starting crawl from {self.start_url} (max_depth={self.max_depth}) ...")
        self._crawl_recursive(self.start_url)
        logging.info(f"Crawl complete. {len(self.faq_data)} FAQ entries found.")
        return self.faq_data

    def _crawl_recursive(self, url: str, depth: int = 0):
        if url in self.visited or depth > self.max_depth:
            return
        self.visited.add(url)
        try:
            response = requests.get(url, headers=self.DEFAULT_HEADERS, timeout=15)
            if not response.ok:
                logging.warning(f"Failed to fetch {url} (status {response.status_code})")
                return
            soup = BeautifulSoup(response.text, "html.parser")
            self._parse_faqs_from_page(soup, url)

            # Get both sidebar and internal links related to support
            links = self._get_all_sidebar_links(soup, url) | self._get_internal_links(soup, url)
            links -= self.visited  # avoid revisiting

            time.sleep(self.sleep_between_requests)
            for link in links:
                self._crawl_recursive(link, depth + 1)
        except Exception as ex:
            logging.error(f"Exception while processing {url}: {ex}")

    @staticmethod
    def _clean(text: str) -> str:
        return " ".join(text.strip().split()) if text else ""

    def _extract_context_category(self, soup: BeautifulSoup) -> str:
        cat = (
            soup.select_one(".active-tax-title")
            or soup.select_one("h1")
            or soup.select_one("h2")
        )
        return self._clean(cat.text) if cat else ""

    def _parse_faqs_from_page(self, soup: BeautifulSoup, url: str) -> bool:
        category = self._extract_context_category(soup)
        found = False
        for tab in soup.select('.faqlist .tab'):
            qelem = tab.select_one('.tab-label span')
            aelem = tab.select_one('.tab-content .content')
            if not qelem or not aelem:
                continue
            question = self._clean(qelem.text)
            answer = aelem.get_text(separator='\n', strip=True)
            self.faq_data.append({
                "category": category,
                "question": question,
                "answer": answer,
                "url": url
            })
            found = True
        return found

    def _is_valid_link(self, href: str) -> bool:
        if not href:
            return False
        href_full = href if href.startswith("http") else urljoin(self.BASE_URL, href)
        parsed = urlparse(href_full)
        if "angelone.in/support" not in href_full:
            return False
        if "/support/hindi" in href_full or "/support/" not in href_full:
            return False
        if parsed.scheme not in ("http", "https"):
            return False
        return True

    def _get_all_sidebar_links(self, soup: BeautifulSoup, curr_url: str) -> Set[str]:
        selectors = [
            "div.sidebar-section a",
            "div.list-item ul.vertical.tabs a",
            "div.shg-search a",
            "li a"
        ]
        links = set()
        for sel in selectors:
            for a in soup.select(sel):
                href = a.get("href")
                if self._is_valid_link(href):
                    full_url = urljoin(curr_url, href)
                    if "/hindi" not in full_url:
                        links.add(full_url)
        return links

    def _get_internal_links(self, soup: BeautifulSoup, curr_url: str) -> Set[str]:
        links = set()
        for a in soup.find_all("a", href=True):
            href = a.get("href")
            if self._is_valid_link(href):
                full_url = urljoin(curr_url, href)
                if "/hindi" not in full_url:
                    links.add(full_url)
        return links

    

    