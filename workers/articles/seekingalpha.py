from . import Article, clean_html_text, ArticleScraper, string_contains, text_to_datetime

import asyncio
import re


IGNORE_HEADLINE = [
    'on the hour',
    'beats on',
    ' misses on revenue'
    'equity offering',
    'Notable earnings',
    ' dividend'
    'leads after hour',
    'Gainers: ',
    ' beats by '
]


IGNORE_TEXT = [
    'Scorecard, Yield Chart',
    'click here',
    'Press Release',
    'ETFs:',
    'See all stocks',
    'now read:',
    'Shelf registration',
    'call starts at',
    'debt offering',
    'Forward yield',
    'for shareholders of record',
    ' principal amount of'
]


class SeekingAlpha(ArticleScraper):

    def __init__(self):
        self.url = 'https://seekingalpha.com'

    async def read_article(self, url):

        article_html = await self._get(url)

        headline_match = re.search(r'itemprop="headline">([^<]+)<', article_html)
        if not headline_match:
            return None
        headline = clean_html_text(headline_match.group(1))

        date_match = re.search(r'content="([\d\-T:Z]+)" itemprop="datePub', article_html)
        date = text_to_datetime(date_match.group(1))

        if string_contains(headline, IGNORE_HEADLINE):
            return None

        text = []

        for bullet_match in re.finditer(r'<p class="bullets_li">([\s\S]+?)<\/p>', article_html):
            bullet_text = clean_html_text(bullet_match.group(1))
            if len(bullet_text) == 0 or string_contains(bullet_text, IGNORE_TEXT):
                continue
            text.append(bullet_text)

        if len(text) == 0:
            return None

        return Article('seekingalpha', headline, date, '\n\n\n'.join(text), self.url + url)

    async def read_news_list(self, pages=15):

        articles = []
        
        article_urls = set()
        for page_num in range(1, pages + 1):
            list_html = await self._get('/market-news/{}'.format(page_num))
            for match in re.finditer(r'href="(\/news\/[^"]+)"', list_html):
                article_urls.add(match.group(1))

        articles = await asyncio.gather(*[self.read_article(url) for url in article_urls])

        return [article for article in articles if article is not None]

    async def read_news(self):
        return await self.read_news_list()