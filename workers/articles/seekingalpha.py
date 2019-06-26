from . import Article, clean_html_text, HEADERS, string_contains

from datetime import datetime
import requests
import time
import re


IGNORE_HEADLINE = [
    'on the hour',
    'beats on',
    ' misses on revenue'
    'equity offering',
    'Notable earnings',
    ' dividend'
    'leads after hour'
]


IGNORE_TEXT = [
    'Scorecard, Yield Chart',
    'click here',
    'Press Release',
    'ETFs:',
    'See all stocks',
    'now read:',
    'Shelf registration',
    'call starts at',
    'debt offering',
    'Forward yield',
    'for shareholders of record',
    ' principal amount of'
]


class SeekingAlpha:

    def __init__(self):
        self.url = 'https://seekingalpha.com'

    def _get(self, url_part):
        time.sleep(0.2)
        return requests.get(self.url + url_part, headers=HEADERS).text

    def read_news_list(self, page_num):

        articles = []
        
        article_urls = set()
        list_html = self._get('/market-news/{}'.format(page_num))
        for match in re.finditer(r'href="(\/news\/[^"]+)"', list_html):
            article_urls.add(match.group(1))

        for url in article_urls:

            article_html = self._get(url)

            headline_match = re.search(r'itemprop="headline">([^<]+)<', article_html)
            if not headline_match:
                continue
            headline = clean_html_text(headline_match.group(1))

            date_match = re.search(r'content="([\d\-T:Z]+)" itemprop="datePub', article_html)
            date = datetime.strptime(date_match.group(1), "%Y-%m-%dT%H:%M:%SZ")

            if string_contains(headline, IGNORE_HEADLINE):
                continue

            text = []

            for bullet_match in re.finditer(r'<p class="bullets_li">([\s\S]+?)<\/p>', article_html):
                bullet_text = clean_html_text(bullet_match.group(1))
                if len(bullet_text) == 0 or string_contains(bullet_text, IGNORE_TEXT):
                    continue
                text.append(bullet_text)

            if len(text) == 0:
                continue

            articles.append(Article('seekingalpha', headline, date, '\n\n\n'.join(text), self.url + url))

        return articles

    def read_news(self):

        all_articles = []
        for i in range(1, 10):
            all_articles.extend(self.read_news_list(i))

        return all_articles