from . import (
    Article, clean_html_text, ArticleScraper, 
    string_contains, text_to_datetime
)

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
    ' beats by ',
    ' reports Q'
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
    ' principal amount of',
    'Developing ...'
]


class SeekingAlpha(ArticleScraper):

    def __init__(self):
        self.url = 'https://seekingalpha.com'

    async def read_article(self, url, parse_headline=True, parse_date=True, parse_text=True):

        article_html = await self._get(url)

        text = []
        headline = ''
        date = None

        if parse_headline:
            headline_match = re.search(r'itemprop="headline">([^<]+)<', article_html)
            if not headline_match:
                return None
            headline = clean_html_text(headline_match.group(1))
            if string_contains(headline, IGNORE_HEADLINE):
                return None

        if parse_date:
            date_match = re.search(r'content="([\d\-T:Z]+)" itemprop="datePub', article_html)
            date = text_to_datetime(date_match.group(1))

        if parse_text:
            for bullet_match in re.finditer(r'<p class="bullets_li">([^<]+?)<\/p>', article_html):
                bullet_text = clean_html_text(bullet_match.group(1))
                if len(bullet_text) == 0 or string_contains(bullet_text, IGNORE_TEXT):
                    continue
                text.append(bullet_text)
            for p_match in re.finditer(r'<p class="p p1">([^<]+?)<\/p>', article_html):
                p_text = clean_html_text(p_match.group(1))
                if len(p_text) == 0 or string_contains(p_text, IGNORE_TEXT):
                    continue
                text.append(p_text)
            if len(text) < 2:
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

    async def read_latest_headlines(self):
        index_html = await self._get('/market-news')
        headlines = []
        for match in re.finditer(r'href="([^"]+?)" class="[\w-]+" sasource="market_news\w+">([^<]+?)<', index_html):
            url = self.url + match.group(1)
            headline = clean_html_text(match.group(2))
            headlines.append((url, headline))
        return 'seekingalpha', headlines

    async def resolve_url_to_content(self, url):
        art = await self.read_article(url.replace(self.url, ''), 
            parse_headline=False, parse_date=False)
        if art is not None:
            return art.content
        return None