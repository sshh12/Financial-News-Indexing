from . import Article, clean_html_text, ArticleScraper, string_contains, text_to_datetime

import asyncio
import re


TOPIC_URLS = [
    '/'
    '/technology',
    '/investing',
    '/markets'
]

IGNORE_TEXT = [
    'is editor of',
    'A confirmation email',
    'Enter a symbol above',
    'Sign up to get',
    'primaryAuthorUrl',
    'article is commentary',
    'To learn more about',
    'Learn more now.',
    'Join Jim Cramer',
    'Do You Understand',
    'Fundamentals of Investing',
    'Read the original',
    'More from: ',
    'Alert PLUS',
    'Can You Name',
    'Additional reporting by',
    'Click here to '
]


class TheStreet(ArticleScraper):

    def __init__(self):
        self.url = 'https://www.thestreet.com'

    async def read_article(self, url):

        if 'video/' in url:
            return None
        
        article_html = await self._get(url)
            
        headline_match = re.search(r'>([^<]+)<\/h1>', article_html)
        if not headline_match:
            return None
        headline = clean_html_text(headline_match.group(1))

        date_match = re.search(r'Publish Date" datetime="([\d\-:T+]+)">', article_html)
        if date_match:
            date = text_to_datetime(date_match.group(1))
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

        return Article('thestreet', headline, date, '\n\n\n'.join(text), self.url + url)

    async def read_news_list(self, topic_urls, pages=5):

        articles = []
        
        article_urls = set()
        for url in topic_urls:
            for i in range(0, pages):
                list_html = await self._get(url + '?page=' + str(i))
                for match in re.finditer(r'href="(\/\w+\/\w+\/[^"]+)"', list_html):
                    article_urls.add(match.group(1))
                for match in re.finditer(r'href="(\/\w+\/[^"]+)"', list_html):
                    article_urls.add(match.group(1))

        articles = await asyncio.gather(*[self.read_article(url) for url in article_urls])

        return [article for article in articles if article is not None]

    async def read_news(self):
        return await self.read_news_list(TOPIC_URLS)
