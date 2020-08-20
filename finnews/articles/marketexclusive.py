from finnews.articles.abs import ArticleScraper
from finnews.articles.utils import clean_html_text
import re


class MarketExclusive(ArticleScraper):
    def __init__(self):
        self.url = "https://marketexclusive.com"

    async def read_latest_headlines(self):
        index_html = await self._get("/category/market-news/")
        headlines = []
        for match in re.finditer(r'<a href="(https:\/\/marketexclusive.com[^"]+?\d+\/\d+\/)">([^<]+?)<', index_html):
            url = match.group(1)
            if "category" in url:
                continue
            headline = clean_html_text(match.group(2))
            headlines.append((url, headline))
        return "marketexclusive", headlines
