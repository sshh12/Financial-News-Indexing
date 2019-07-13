from . import Article, clean_html_text, ArticleScraper, string_contains, text_to_datetime

import asyncio
import re


TOPIC_URLS = [
    '/',
    '/category/technology-news',
    '/category/markets-news',
    '/category/business-news',
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
    '/advertising'
]

IGNORE_TEXT = [
    'photo via',
    ' image via ',
    'via CoinDesk',
    'CoinDesk is a',
    'Edit: '
]


class CoinDesk(ArticleScraper):

    def __init__(self):
        self.url = 'https://www.coindesk.com/'

    async def read_article(self, url):
        
        article_html = await self._get(url)
            
        headline_match = re.search(r'<h1>([^<]+)<\/h1>', article_html)
        if not headline_match:
            return None
        headline = clean_html_text(headline_match.group(1))

        date_match = re.search(r'<span>(\w+ \d+, \d+ at \d+:\d+ \w+)<\/span>', article_html)
        if date_match:
            date = text_to_datetime(date_match.group(1).replace(' at ', ' '))
        else:
            return None

        text = []

        for p_match in re.finditer(r'<p>([\s\S]+?)<\/p>', article_html):
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
            for match in re.finditer(r'coindesk.com(\/[\w\-\/]+)"', list_html):
                if not string_contains(match.group(1), IGNORE_URLS):
                    article_urls.add(match.group(1))

        articles = await asyncio.gather(*[self.read_article(url) for url in article_urls])

        return [article for article in articles if article is not None]

    async def read_news(self):
        return await self.read_news_list(TOPIC_URLS)