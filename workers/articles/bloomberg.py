from . import Article, clean_html_text, HEADERS, text_to_datetime

import requests
from requests import Session
import time
import re


PAGES = [
    '/'
    '/politics',
    '/markets',
    '/technology'
]


class Bloomberg:

    def __init__(self):
        self.url = 'https://www.bloomberg.com'
        self.sess = Session()

    def _get(self, url_part):
        time.sleep(1)
        headers = HEADERS.copy()
        headers['authority'] = 'www.bloomberg.com'
        headers['path'] = url_part
        headers['cache-control'] = 'no-cache'
        headers['accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3'
        return self.sess.get(self.url + url_part, headers=headers).text

    def read_news_list(self, topic_urls):

        articles = []
        
        article_urls = set()
        for url in topic_urls:
            list_html = self._get(url)
            for match in re.finditer(r'href="(\/news\/articles\/[^"]+)"', list_html):
                article_urls.add(match.group(1))

        if len(article_urls) == 0:
            print('Bloomberg blocked client ):')

        for url in article_urls:

            article_html = self._get(url)

            headline_match = re.search(r'>([^<]+)<\/h1>', article_html)
            if not headline_match:
                continue
            headline = clean_html_text(headline_match.group(1))

            date_match = re.search(r'itemprop="datePublished" datetime="([\d\-T:\.Z]+)"', article_html)
            date = text_to_datetime(date_match.group(1))

            text = []

            for paragraph_match in re.finditer(r'<p>([\s\S]+?)<\/p>', article_html):
                p_text = clean_html_text(paragraph_match.group(1))
                if len(p_text) != 0:
                    text.append(p_text)

            if len(text) == 0:
                continue

            articles.append(Article('bloomberg', headline, date, '\n\n\n'.join(text), self.url + url))

        return articles

    def read_news(self):
        return self.read_news_list(PAGES)