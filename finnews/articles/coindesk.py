from . import Article, clean_html_text, ArticleScraper, string_contains, text_to_datetime

import asyncio
import re


TOPIC_URLS = [
    '/',
    '/news',
    '/features',
    '/opinion'
    '/category/tech',
    '/category/markets',
    '/category/business',
]

IGNORE_URLS = [
    '/editorial-policy',
    '/privacy-policy',
    '/page/',
    '/feed',
    '/blog',
    '/press',
    '/events',
    '/employer-details/',
    'coindesk-inc',
    '/terms-conditions',
    '/about',
    '/newsletters',
    '/category/',
    '/advertising',
    '/data',
    '/learn',
    '/search',
    '/webinars',
    '/video',
    '/privacy',
    '/ico-calendar',
    '/bitcoin-events',
    '/news',
    '/calculator',
    '/terms',
    '/crypto-investment-research',
    '/features',
    '/opinion',
    '/coindesk-api',
    '/tag',
    '/author'
]

IGNORE_TEXT = [
    'photo via',
    ' image via ',
    'via CoinDesk',
    'CoinDesk is a',
    'Edit: ',
    'contributed reporting',
    'See also: '
]


class CoinDesk(ArticleScraper):

    def __init__(self):
        self.url = 'https://www.coindesk.com'

    async def read_article(self, url):
        
        article_html = await self._get(url)
            
        headline_match = re.search(r'<h1 class="heading\s*">([^<]+)<\/h1>', article_html)
        if not headline_match:
            return None
        headline = clean_html_text(headline_match.group(1))

        date_match = re.search(r'<time dateTime="([^"]+?)">', article_html)
        if not date_match:
            return None
        date = text_to_datetime(date_match.group(1))

        text = []

        for p_match in re.finditer(r'<p class="text\s*">([\s\S]+?)<\/p>', article_html):
            paragraph = clean_html_text(p_match.group(1))
            if paragraph.count(' ') <= 2 or string_contains(paragraph, IGNORE_TEXT):
                continue
            text.append(paragraph)

        if len(text) == 0:
            return None

        return Article('coindesk', headline, date, '\n\n\n'.join(text), self.url + url)

    async def read_news_list(self, topic_urls, pages=5):

        articles = []
        
        article_urls = set()
        for url in topic_urls:
            list_html = await self._get(url)
            for match in re.finditer(r'href="(\/[\w\-\/]+)"', list_html):
                if not string_contains(match.group(1), IGNORE_URLS):
                    article_urls.add(match.group(1))

        articles = await asyncio.gather(*[self.read_article(url) for url in article_urls])

        return [article for article in articles if article is not None]

    async def read_news(self):
        return await self.read_news_list(TOPIC_URLS)