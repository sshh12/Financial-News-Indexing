from finnews.articles.abs import ArticleScraper
from finnews.articles.utils import clean_html_text
import re
import json
import re


class USBLS(ArticleScraper):
    def __init__(self):
        self.url = "https://www.bls.gov/opub/ted/year.htm"

    async def read_latest_headlines(self):
        index_html = await self._get("/opub/ted/year.htm")
        headlines = []
        for match in re.finditer(r'<a href="([^"]+?)" title="([^"]+?)"', index_html):
            url = self.url + match.group(1)
            headline = clean_html_text(match.group(2))
            headlines.append((url, headline))
        return "usbls", headlines
