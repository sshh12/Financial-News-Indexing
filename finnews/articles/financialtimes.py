from finnews.articles.abs import ArticleScraper
from finnews.articles.utils import clean_html_text, url_to_n3karticle
import re

HEADLINE_REGEX = r'<a href="(\/content\/[\w\d\-]+?)" data-trackable="heading[^>]+?>([^<]+?)<\/a>'


class FinancialTimes(ArticleScraper):
    def __init__(self):
        self.url = "https://www.ft.com"

    async def read_latest_headlines(self):
        comp_html = await self._get("/companies")
        us_html = await self._get("/world/us")
        headlines = []
        urls = set()
        for match in re.finditer(HEADLINE_REGEX, comp_html):
            url = self.url + match.group(1)
            urls.add(url)
            headline = clean_html_text(match.group(2))
            headlines.append((url, headline))
        for match in re.finditer(HEADLINE_REGEX, us_html):
            url = self.url + match.group(1)
            if url in urls:
                continue
            headline = clean_html_text(match.group(2))
            headlines.append((url, headline))
        return "financialtimes", headlines
