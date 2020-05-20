from . import Article, clean_html_text, ArticleScraper, url_to_n3karticle

import asyncio
import re


TRIM_AT = []


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

    async def resolve_url_to_content(self, url):
        art = url_to_n3karticle(url)
        text = clean_html_text(art.text)
        if len(text) < 100:
            return None
        for trim_token in TRIM_AT:
            try:
                idx = text.index(trim_token)
            except:
                continue
            text = text[:idx].strip()
        return text
