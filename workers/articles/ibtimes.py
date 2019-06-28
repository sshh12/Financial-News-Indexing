from . import Article, clean_html_text, HEADERS, string_contains, text_to_datetime

import requests
import time
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


class IBTimes:

    def __init__(self):
        self.url = 'https://www.ibtimes.com'

    def _get(self, url_part):
        time.sleep(0.2)
        return requests.get(self.url + url_part, headers=HEADERS).text

    def read_news_list(self, topic_urls, pages=4):

        articles = []
        
        article_urls = set()
        for url in topic_urls:
            for i in range(pages):
                list_html = self._get(url + '?page=' + str(i))
                for match in re.finditer(r'"(\/[\w\-]+\d{4,12})"', list_html):
                    article_urls.add(match.group(1))

        for url in article_urls:

            article_html = self._get(url)

            headline_match = re.search(r'itemprop="headline">([^<]+)<\/h1>', article_html)
            if not headline_match:
                continue
            headline = clean_html_text(headline_match.group(1))

            if string_contains(headline, IGNORE_TITLES):
                continue

            date_match = re.search(r'datePublished" datetime="([\d\-:T]+)"', article_html)
            date = text_to_datetime(date_match.group(1))

            text = []

            for p_match in re.finditer(r'<p>([\s\S]+?)<\/p>', article_html):
                paragraph = clean_html_text(p_match.group(1))
                if paragraph.count(' ') <= 1 or string_contains(paragraph, IGNORE_TEXT):
                    continue
                text.append(paragraph)

            if len(text) == 0:
                continue

            articles.append(Article('ibtimes', headline, date, '\n\n\n'.join(text), self.url + url))

        return articles

    def read_news(self):
        return self.read_news_list(TOPIC_URLS)