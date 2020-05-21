from . import Article, clean_html_text, ArticleScraper
import re


class AlphaStockNews(ArticleScraper):

    def __init__(self):
        self.url = 'https://alphastocknews.com'

    async def read_latest_headlines(self):
        index_html = await self._get('/')
        headlines = []
        for match in re.finditer(r'title"><a\s*href="([^"]+?)"[^>]+?>([^<]+?)<', index_html):
            url = match.group(1)
            headline = clean_html_text(match.group(2))
            headlines.append((url, headline))
        return 'alphastocknews', headlines
