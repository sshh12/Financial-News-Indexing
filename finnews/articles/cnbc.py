from . import Article, clean_html_text, ArticleScraper, string_contains, text_to_datetime

import asyncio
import re


TOPIC_URLS = [
    '/markets',
    '/us-markets',
    '/economy',
    '/health-and-science',
    '/aerospace-defense'
    '/business',
    '/investing',
    '/technology',
    '/enterprise',
    '/politics'
]

IGNORE_TEXT = [
    '@cnbc.com',
    'Questions for',
    'Keep Me Logged In',
    'Source: ',
    'contributed to this report',
    'Disclosure: ',
    'Watch: ',
    'Twitter - Facebook',
    'contributed to this story'
]


class CNBC(ArticleScraper):

    def __init__(self):
        self.url = 'https://www.cnbc.com'

    async def read_article(self, url):
        
        article_html = await self._get(url)
            
        headline_match = re.search(r'ArticleHeader-headline">([^<]+)<\/h1>', article_html)
        if not headline_match:
            return None
        headline = clean_html_text(headline_match.group(1))

        full_date_match = re.search(r'Published \w+, (\w+ \d+ \d+) <span class="ArticleHeader-datetimeDivider"><\/span> (\d+:\d+ \w+ \w+)<\/time>', article_html)
        rel_date_match = re.search(r'published-timestamp">Published (\d hours ago)<\/time>', article_html)
        if full_date_match:
            date = text_to_datetime(full_date_match.group(1) + ' ' + full_date_match.group(2))
        elif rel_date_match:
            date = text_to_datetime(rel_date_match.group(1))
        else:
            return None

        text = []

        for p_match in re.finditer(r'<p>([\s\S]+?)<\/p>', article_html):
            paragraph = clean_html_text(p_match.group(1))
            if paragraph.count(' ') <= 1 or string_contains(paragraph, IGNORE_TEXT):
                continue
            text.append(paragraph)

        if len(text) == 0:
            return None

        return Article('cnbc', headline, date, '\n\n\n'.join(text), self.url + url)

    async def read_news_list(self, topic_urls):

        articles = []
        
        article_urls = set()
        for url in topic_urls:
            list_html = await self._get(url)
            for match in re.finditer(r'href=\'(\/\d{4}[^\']+)\'', list_html):
                article_urls.add(match.group(1))
            for match in re.finditer(r'href="https:\/\/www.cnbc.com(\/\d{4}[^"]+)"', list_html):
                article_urls.add(match.group(1))

        articles = await asyncio.gather(*[self.read_article(url) for url in article_urls])

        return [article for article in articles if article is not None]

    async def read_news(self):
        return await self.read_news_list(TOPIC_URLS)