from . import Article, clean_html_text, ArticleScraper, string_contains, text_to_datetime

import asyncio
import re


TOPIC_URLS = [
    '/business',
    '/world',
    '/business/tech',
    '/data/markets/',
    '/specials/space-science'
]

IGNORE_TEXT = [
    '@cnn.com',
]


class CNN(ArticleScraper):

    def __init__(self):
        self.url = 'https://www.cnn.com'

    async def read_article(self, url):
        
        article_html = await self._get(url)
            
        headline_match = re.search(r'pg-headline">([^<]+)<\/h1>', article_html)
        if not headline_match:
            return None
        headline = clean_html_text(headline_match.group(1))

        update_date_match = re.search(r'Updated (\d+:\d+ \w+ \w+), \w+ (\w+ \d+, \d+)', article_html)
        if update_date_match:
            date = text_to_datetime(update_date_match.group(2) + ' ' + update_date_match.group(1))
        else:
            return None

        text = []

        for p_match in re.finditer(r'<(\w{1,3}) class="zn-body__paragraph[ a-z]*">([\s\S]+?)<\/\1>', article_html):
            paragraph = clean_html_text(p_match.group(2))
            paragraph = re.sub(r'\)([A-Z])', r') - \1', paragraph)
            if paragraph.count(' ') <= 1 or string_contains(paragraph, IGNORE_TEXT):
                continue
            text.append(paragraph)

        if len(text) == 0:
            return None

        return Article('cnn', headline, date, '\n\n\n'.join(text), self.url + url)

    async def read_news_list(self, topic_urls):

        articles = []
        
        article_urls = set()
        for url in topic_urls:
            list_html = await self._get(url)
            for match in re.finditer(r'href="(\/\d{4}[^"]+)"', list_html):
                article_urls.add(match.group(1))

        articles = await asyncio.gather(*[self.read_article(url) for url in article_urls])

        return [article for article in articles if article is not None]

    async def read_news(self):
        return await self.read_news_list(TOPIC_URLS)