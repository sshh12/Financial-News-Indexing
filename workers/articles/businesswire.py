from . import Article, clean_html_text, ArticleScraper

import asyncio
import re


class BusinessWire(ArticleScraper):

    def __init__(self):
        self.url = 'https://www.businesswire.com'

    async def read_latest_headlines(self):
        index_html = await self._get('/portal/site/home/news/')
        headlines = []
        for match in re.finditer(r'bwTitleLink"\s*href="([^"]+?)"><span itemprop="headline">([^<]+?)<', index_html):
            url = self.url + match.group(1)
            headline = clean_html_text(match.group(2))
            headlines.append((url, headline))
        return 'businesswire', headlines
