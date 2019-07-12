from . import Article, clean_html_text, ArticleScraper, string_contains, text_to_datetime

import asyncio
import re


TOPIC_URLS = [
    '/',
    '/sai',
    '/clusterstock',
    '/transportation',
    '/politics'
    '/moneygame',
    '/science',
    '/retail',
    '/enterprise'
]

IGNORE_TEXT = [
    '<div',
    'data-authors',
    'Read more: ',
    'Read: ',
    'Getty Images',
    'Get the latest',
    'full, the report',
    'takeaways from the report',
    'getting the full report?',
    'The choice is yours.',
    'Business Insider Intelligence',
    'a brand new FREE report',
    'This is an opinion column',
    'Keep reading to see',
    'post has been translated',
    'Subscribe to our newsletter',
    'Source: ',
    'Click here to ',
    'Got a tip?',
    '@businessinsider.com',
    ' Join here.',
    'AP Photo',
    'If you are a '
]


class BusinessInsider(ArticleScraper):

    def __init__(self):
        self.url = 'https://www.businessinsider.com'

    async def read_article(self, url):
        
        article_html = await self._get(url)
            
        headline_match = re.search(r'>([^<]+)<\/h1>', article_html)
        if not headline_match:
            return None
        headline = clean_html_text(headline_match.group(1))

        if headline == 'Whoops!':
            return None

        date_match = re.search(r'byline-timestamp" data-timestamp="([\-+\dT:]+)"', article_html)
        if date_match:
            date = text_to_datetime(date_match.group(1))
        else:
            return None

        text = []

        for p_match in re.finditer(r'<p\s+class="">([\s\S]+?)<\/p>', article_html):
            paragraph = clean_html_text(p_match.group(1))
            if paragraph.count(' ') <= 2 or string_contains(paragraph, IGNORE_TEXT):
                continue
            text.append(paragraph)

        if len(text) == 0:
            return None

        return Article('businessinsider', headline, date, '\n\n\n'.join(text), self.url + url)

    async def read_news_list(self, topic_urls, pages=5):

        articles = []
        
        article_urls = set()
        for url in topic_urls:
            list_html = await self._get(url)
            for match in re.finditer(r'businessinsider.com(\/[^\/&\?="]{8,})"', list_html):
                article_urls.add(match.group(1))

        articles = await asyncio.gather(*[self.read_article(url) for url in article_urls])

        return [article for article in articles if article is not None]

    async def read_news(self):
        return await self.read_news_list(TOPIC_URLS)