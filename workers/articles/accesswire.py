from . import Article, clean_html_text, ArticleScraper
import re


class AccessWire(ArticleScraper):

    def __init__(self):
        self.url = 'https://www.accesswire.com'

    async def read_latest_headlines(self):
        index_html = await self._get('/api/newsroom.ashx')
        headlines = []
        for match in re.finditer(r'headlinelink"><a href="([^"]+?)" class="headlinelink">([^"]+?)<', index_html):
            url = match.group(1)
            headline = clean_html_text(match.group(2))
            headlines.append((url, headline))
        return 'accesswire', headlines
