from . import Article, clean_html_text, HEADERS, string_contains, text_to_datetime

import requests
import time
import re


TOPIC_URLS = [
    '/',
    '/tech',
    '/science',
    '/entertainment',
    '/microsoft',
    '/amazon',
    '/samsung',
    '/privacy',
    '/mobile',
    '/apple',
    '/tesla',
    '/google'
    '/policy',
    '/ai-artificial-intelligence'
]

IGNORE_TEXT = [
    '<section',
    'This article has been'
]


class Verge:

    def __init__(self):
        self.url = 'https://www.theverge.com'

    def _get(self, url_part):
        time.sleep(0.2)
        return requests.get(self.url + url_part, headers=HEADERS).text

    def read_news_list(self, topic_urls):

        articles = []
        
        article_urls = set()
        for url in topic_urls:
            list_html = self._get(url)
            for match in re.finditer(r'theverge.com(\/\d{4}\/[^"]+)"', list_html):
                article_urls.add(match.group(1))

        for url in article_urls:

            article_html = self._get(url)

            headline_match = re.search(r'title">([^<]+)<\/h1>', article_html)
            if not headline_match:
                continue
            headline = clean_html_text(headline_match.group(1))

            date_match = re.search(r'c-byline__item" data-ui="timestamp" datetime="([\d\-T:+]+)"', article_html)
            if not date_match:
                continue
            date = text_to_datetime(date_match.group(1))

            text = []

            for p_match in re.finditer(r'<p id="\w+">([\s\S]+?)<\/p>', article_html):
                paragraph = clean_html_text(p_match.group(1))
                if paragraph.count(' ') <= 1 or string_contains(paragraph, IGNORE_TEXT):
                    continue
                text.append(paragraph)

            if len(text) == 0:
                continue

            articles.append(Article('verge', headline, date, '\n\n\n'.join(text), self.url + url))

        return articles

    def read_news(self):
        return self.read_news_list(TOPIC_URLS)