from . import Article, ArticleScraper, clean_html_text, text_to_datetime

import asyncio
import re


PAGES = [
    '/'
    '/politics',
    '/markets',
    '/technology'
]


class Bloomberg(ArticleScraper):

    def __init__(self):
        self.url = 'https://www.bloomberg.com'

    async def read_article(self, url):

        article_html = await self._get(url)

        headline_match = re.search(r'>([^<]+)<\/h1>', article_html)
        if not headline_match:
            return None
        headline = clean_html_text(headline_match.group(1))

        date_match = re.search(r'itemprop="datePublished" datetime="([\d\-T:\.Z]+)"', article_html)
        date = text_to_datetime(date_match.group(1))

        text = []

        for paragraph_match in re.finditer(r'<p>([\s\S]+?)<\/p>', article_html):
            p_text = clean_html_text(paragraph_match.group(1))
            if len(p_text) != 0:
                text.append(p_text)

        if len(text) == 0:
            return None

        return Article('bloomberg', headline, date, '\n\n\n'.join(text), self.url + url)

    async def read_news_list(self, topic_urls):

        articles = []
        
        article_urls = set()
        for url in topic_urls:
            list_html = await self._get(url)
            for match in re.finditer(r'href="(\/news\/articles\/[^"]+)"', list_html):
                article_urls.add(match.group(1))

        articles = await asyncio.gather(*[self.read_article(url) for url in article_urls])

        return [article for article in articles if article is not None]

    def read_news(self):
        return self.read_news_list(PAGES)