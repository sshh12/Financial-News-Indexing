from finnews.articles.abs import ArticleScraper
from finnews.articles.utils import clean_html_text, url_to_n3karticle, string_contains
import re

IGNORE_ITEMS = [
    'Read more on',
    'Subscribe to'
]


class CNBC(ArticleScraper):
    def __init__(self):
        self.url = "https://www.cnbc.com"

    async def read_latest_headlines(self):
        index_html = await self._get("/")
        headlines = []
        for match in re.finditer(r'LatestNews-headline"><a href="(http[^"]+?)" title="">([^<]+?)<', index_html):
            url = match.group(1)
            headline = clean_html_text(match.group(2))
            headlines.append((url, headline))
        return "cnbc", headlines

    async def resolve_url_to_content(self, url):
        if not url.startswith(self.url):
            return None
        art = url_to_n3karticle(url)
        text = clean_html_text(art.text)
        filtered_text = "\n".join([line for line in text.split("\n") if not string_contains(line, IGNORE_ITEMS)])
        return filtered_text
