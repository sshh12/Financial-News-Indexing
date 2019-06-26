from . import Article, clean_html_text, HEADERS, text_to_datetime, string_contains

from datetime import datetime
import requests
import time
import re


IGNORE_TEXT = [
    'Read: ',
    'Now read: ',
    'See: ',
    'And see: ',
    'Read more: ',
    'Check out: '
]


class MarketWatch:

    def __init__(self):
        self.url = 'https://www.marketwatch.com'

    def _get(self, url_part):
        time.sleep(0.2)
        return requests.get(self.url + url_part, headers=HEADERS).text

    def read_news_list(self, offsets=[0]):

        articles = []
        
        article_urls = set()
        for offset in offsets:
            list_html = self._get('/latest-news?offset={}&position=1.1&partial=true'.format(offset))
            for match in re.finditer(r'href="https:\/\/www.marketwatch.com(\/story[^"]+)"', list_html):
                article_urls.add(match.group(1))

        for url in article_urls:

            article_html = self._get(url)

            headline_match = re.search(r'itemprop="headline">([^<]+)<', article_html)
            if not headline_match:
                continue
            headline = clean_html_text(headline_match.group(1))

            date_match = re.search(r'>(\w+ \d+, \d+ \d+:\d+ [\.apm]+ \w+)<', article_html)
            date = text_to_datetime(date_match.group(1))

            text = []

            start_idx = article_html.index('articleBody')
            try:
                end_idx = article_html.index('author-commentPromo')
            except ValueError:
                end_idx = len(article_html)
            content_html = article_html[start_idx:end_idx]
            for paragraph_match in re.finditer(r'<p>([\s\S]+?)<\/p>', content_html):
                p = clean_html_text(paragraph_match.group(1))
                if len(p) >= 30 and not string_contains(p, IGNORE_TEXT):
                    text.append(p)

            articles.append(Article('marketwatch', headline, date, '\n\n\n'.join(text), self.url + url))

        return articles

    def read_news(self):
        return self.read_news_list(range(0, 100, 20))