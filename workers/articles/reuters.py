from . import Article, clean_html_text, ArticleScraper, text_to_datetime

import asyncio
import re


TOPIC_URLS = [
    'businessnews', 
    'marketsNews', 
    'technologynews', 
    'healthnews', 
    'banks', 
    'aerospace-defense', 
    'innovationintellectualproperty', 
    'environmentnews', 
    'worldnews',
    'esgnews'
]


class Reuters(ArticleScraper):

    def __init__(self):
        self.url = 'https://www.reuters.com'

    async def read_article(self, url):
        
        article_html = await self._get(url)

        date_match = re.search(r'(\w+ \d+, \d{4}) \/\s+(\d+:\d+ \w+) ', article_html)
        headline_match = re.search(r'ArticleHeader_headline">([^<]+)<\/h1>', article_html)
        if not date_match or not headline_match:
            return None

        headline = clean_html_text(headline_match.group(1))
        date = text_to_datetime(date_match.group(1) + ' ' + date_match.group(2))

        text = []
        start_idx = article_html.index('StandardArticleBody_body')
        try:
            end_idx = article_html.index('Attribution_container')
        except ValueError:
            end_idx = len(article_html)
        content_html = article_html[start_idx:end_idx]
        for paragraph_match in re.finditer(r'<p>([^<]+)<\/p>', content_html):
            text.append(clean_html_text(paragraph_match.group(1)))

        if len(text) == 0:
            return None

        return Article('reuters', headline, date, '\n\n\n'.join(text), self.url + url)

    async def read_news_list(self, topics):

        articles = []
        
        article_urls = set()
        for topic_url in topics:
            list_html = await self._get('/news/archive/{}?view=page&page=1&pageSize=10'.format(topic_url))
            for match in re.finditer(r'href="(\/article\/[^"]+)"', list_html):
                article_urls.add(match.group(1))

        articles = await asyncio.gather(*[self.read_article(url) for url in article_urls])

        return [article for article in articles if article is not None]

    async def read_news(self):
        return await self.read_news_list(TOPIC_URLS)