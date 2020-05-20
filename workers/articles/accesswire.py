from . import Article, clean_html_text, ArticleScraper
import json
import re


TRIM_AT = [
    'Forward-Looking Statements'
]


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

    async def resolve_url_to_content(self, url):
        id_ = url.split('.com')[1].split('/')[1]
        resp = await self._get('/users/api/publicRelease?id={}'.format(id_))
        data = json.loads(resp)
        text = clean_html_text(data['data']['body'])
        if len(text) < 100:
            return None
        for trim_token in TRIM_AT:
            try:
                idx = text.index(trim_token)
            except:
                continue
            text = text[:idx].strip()
        return text
