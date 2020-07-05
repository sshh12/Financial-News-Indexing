from . import Article, clean_html_text, ArticleScraper, url_to_n3karticle
import asyncio
import re


TRIM_AT = [
    'Forward-Looking Statements',
    'This press release contains forward-looking statements',
    'Safe Harbor Statement'
]


class BusinessWire(ArticleScraper):

    def __init__(self):
        self.url = 'https://www.businesswire.com'

    async def read_latest_headlines(self):
        index_html = await self._get('/portal/site/home/news/')
        headlines = []
        for match in re.finditer(r'bwTitleLink"\s*href="([^"]+?)"><span itemprop="headline">([^<]+?)<', index_html):
            url = self.url + match.group(1)
            if url.split('/')[-1] in ['zh-CN', 'ja', 'zh-HK']:
                continue
            headline = clean_html_text(match.group(2))
            headlines.append((url, headline))
        return 'businesswire', headlines

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
