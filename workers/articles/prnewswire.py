from . import Article, clean_html_text, ArticleScraper

import asyncio
import re


class PRNewsWire(ArticleScraper):

    def __init__(self):
        self.url = 'https://www.prnewswire.com'

    async def read_latest_headlines(self):
        index_html = await self._get('/news-releases/news-releases-list/')
        headlines = []
        for match in re.finditer(r'news-release" href="([^"]+?)" title="[^"]*?">([^<]+?)<', index_html):
            url = self.url + match.group(1)
            headline = clean_html_text(match.group(2))
            headlines.append((url, headline))
        return 'prnewswire', headlines
