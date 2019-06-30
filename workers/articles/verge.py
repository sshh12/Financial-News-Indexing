from . import Article, clean_html_text, ArticleScraper, string_contains, text_to_datetime

import asyncio
import re


TOPIC_URLS = [
    '/',
    '/tech',
    '/science',
    '/entertainment',
    '/microsoft',
    '/amazon',
    '/samsung',
    '/privacy',
    '/mobile',
    '/apple',
    '/tesla',
    '/google'
    '/policy',
    '/ai-artificial-intelligence'
]

IGNORE_TEXT = [
    '<section',
    'This article has been'
]


class Verge(ArticleScraper):

    def __init__(self):
        self.url = 'https://www.theverge.com'

    async def read_article(self, url):

        article_html = await self._get(url)

        headline_match = re.search(r'title">([^<]+)<\/h1>', article_html)
        if not headline_match:
            return None
        headline = clean_html_text(headline_match.group(1))

        date_match = re.search(r'c-byline__item" data-ui="timestamp" datetime="([\d\-T:+]+)"', article_html)
        if not date_match:
            return None
        date = text_to_datetime(date_match.group(1))

        text = []

        for p_match in re.finditer(r'<p id="\w+">([\s\S]+?)<\/p>', article_html):
            paragraph = clean_html_text(p_match.group(1))
            if paragraph.count(' ') <= 1 or string_contains(paragraph, IGNORE_TEXT):
                continue
            text.append(paragraph)

        if len(text) == 0:
            return None

        return Article('verge', headline, date, '\n\n\n'.join(text), self.url + url)

    async def read_news_list(self, topic_urls):

        articles = []
        
        article_urls = set()
        for url in topic_urls:
            list_html = await self._get(url)
            for match in re.finditer(r'theverge.com(\/\d{4}\/[^"]+)"', list_html):
                article_urls.add(match.group(1))

        articles = await asyncio.gather(*[self.read_article(url) for url in article_urls])

        return [article for article in articles if article is not None]

    async def read_news(self):
        return await self.read_news_list(TOPIC_URLS)