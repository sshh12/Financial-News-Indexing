from finnews.articles.abs import ArticleScraper
from finnews.articles.utils import clean_html_text
import re


class Forbes(ArticleScraper):
    def __init__(self):
        self.url = "https://www.forbes.com"

    async def read_latest_headlines(self):
        index_html = await self._get("/news/")
        headlines = []
        for match in re.finditer(r'href="(https:\/\/www.forbes.com\/sites\/\w+\/\d+[^"]+?)">([^<]+?)<', index_html):
            url = match.group(1)
            headline = clean_html_text(match.group(2))
            headlines.append((url, headline))
        return "forbes", headlines
