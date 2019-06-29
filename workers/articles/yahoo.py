from . import Article, clean_html_text, ArticleScraper, string_contains, text_to_datetime

import asyncio
import re


IGNORE_TEXT = [
    '<span',
    '<svg',
    '<input',
    'No matching results',
    'Tip: ',
    '<a',
    'Give feedback on',
    'Check out our'
    'WATCH: ',
    'SEE ALSO: '
    'has a disclosure policy',
    'More From ',
    'Image source: ',
    '©',
    'Benzinga.com',
    'See more from ',
    'Latest Ratings for ',
    'Stock Analysis Report',
    'To read this article',
    'Want the latest recommendations',
    'See This Ticker',
    'Data source:',
    'Reporting by ',
    'Check Out: '
]


class Yahoo(ArticleScraper):

    def __init__(self):
        self.url = 'https://finance.yahoo.com'

    async def read_article(self, url):
        
        article_html = await self._get(url)
            
        headline_match = re.search(r'>([^<]+)<\/h1>', article_html)
        if not headline_match:
            return None
        headline = clean_html_text(headline_match.group(1))

        date_match = re.search(r'datetime="([\d\-T:Z\.]+)" itemprop="datePublished"', article_html)
        if date_match:
            date = text_to_datetime(date_match.group(1))
        else:
            return None

        text = []

        for p_match in re.finditer(r'<(span|p) [^>]+>([\s\S]+?)<\/(span|p)>', article_html):
            paragraph = clean_html_text(p_match.group(2))
            if paragraph.count(' ') <= 2 or string_contains(paragraph, IGNORE_TEXT) or paragraph[0] == ')':
                continue
            if 'list is empty' in paragraph:
                break
            text.append(paragraph)

        if len(text) == 0:
            return None

        return Article('yahoo', headline, date, '\n\n\n'.join(text), self.url + url)

    async def read_news_list(self):

        articles = []
        
        article_urls = set()
        list_html = await self._get('/rss/topstories')
        for match in re.finditer(r'finance.yahoo.com(\/news\/[\w\-]+.html)', list_html):
            article_urls.add(match.group(1))

        articles = await asyncio.gather(*[self.read_article(url) for url in article_urls])

        return [article for article in articles if article is not None]

    async def read_news(self):
        return await self.read_news_list()