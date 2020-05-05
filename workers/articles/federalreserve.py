from . import Article, clean_html_text, ArticleScraper

import asyncio
import json
import re


class FederalReserve(ArticleScraper):

    def __init__(self):
        self.url = 'https://www.federalreserve.gov'

    async def read_latest_headlines(self):
        index_data = await self._get('/json/ne-press.json')
        index_json = json.loads(index_data.encode('ascii', 'ignore').decode('ascii'))
        headlines = []
        for item in index_json:
            if 't' not in item:
                continue
            url = self.url + item['l']
            headline = clean_html_text(item['t'])
            headlines.append((url, headline))
        return 'federalreserve', headlines
