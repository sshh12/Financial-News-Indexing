from . import Article, clean_html_text, ArticleScraper, string_contains, text_to_datetime

import asyncio
import re


TOPIC_URLS = [
    '/business',
    '/technology',
    '/world',
    '/national'
]

IGNORE_TITLES = [
    'Infographic:',
    ' [WATCH]',
    ' [PHOTOS]'
]

IGNORE_TEXT = [
    'Photo: ',
    'Pictured: '
    'Wikipedia/Wikimedia Commons'
]


class IBTimes(ArticleScraper):

    def __init__(self):
        self.url = 'https://www.ibtimes.com'

    async def read_article(self, url):
        
        article_html = await self._get(url)

        headline_match = re.search(r'itemprop="headline">([^<]+)<\/h1>', article_html)
        if not headline_match:
            return None
        headline = clean_html_text(headline_match.group(1))

        if string_contains(headline, IGNORE_TITLES):
            return None

        date_match = re.search(r'datePublished" datetime="([\d\-:T]+)"', article_html)
        if not date_match:
            return None
        date = text_to_datetime(date_match.group(1))

        text = []

        for p_match in re.finditer(r'<p>([\s\S]+?)<\/p>', article_html):
            paragraph = clean_html_text(p_match.group(1))
            if paragraph.count(' ') <= 1 or string_contains(paragraph, IGNORE_TEXT):
                return None
            text.append(paragraph)

        if len(text) == 0:
            return None

        return Article('ibtimes', headline, date, '\n\n\n'.join(text), self.url + url)

    async def read_news_list(self, topic_urls, pages=4):

        articles = []
        
        article_urls = set()
        for url in topic_urls:
            for i in range(pages):
                list_html = await self._get(url + '?page=' + str(i))
                for match in re.finditer(r'"(\/[\w\-]+\d{4,12})"', list_html):
                    article_urls.add(match.group(1))

        articles = await asyncio.gather(*[self.read_article(url) for url in article_urls])

        return [article for article in articles if article is not None]

    async def read_news(self):
        return await self.read_news_list(TOPIC_URLS)