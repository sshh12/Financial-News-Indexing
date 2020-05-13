from . import Article, clean_html_text, ArticleScraper

import asyncio
import re


class GlobeNewsWire(ArticleScraper):

    def __init__(self):
        self.url = 'https://www.globenewswire.com'

    async def read_latest_headlines(self):
        index_html = await self._get('/Index')
        headlines = []
        for match in re.finditer(r'title">([^<]+?)<\/p>[\s\S]+?title16px"><a href="([^"]+?)">([^<]+?)<', index_html):
            company = match.group(1)
            url = self.url + match.group(2)
            headline = clean_html_text(company + ' -- ' + match.group(3))
            headlines.append((url, headline))
        return 'globenewswire', headlines
