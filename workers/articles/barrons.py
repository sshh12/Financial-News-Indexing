from . import Article, clean_html_text, HEADERS, string_contains, text_to_datetime

from datetime import datetime
import requests
import time
import re


IGNORE_TEXT = [
    'This copy is for your personal',
    ' Write to ',
    'Read: ',
    'Read more: ',
    ' All Rights Reserved',
    'barrons.com',
    'dowjones.com',
    'Write to '
]


class Barrons:

    def __init__(self):
        self.url = 'https://www.barrons.com'

    def _get(self, url_part):
        time.sleep(0.2)
        return requests.get(self.url + url_part, headers=HEADERS).text

    def read_news_list(self, pages=5):

        articles = []
        
        article_urls = set()
        for i in range(1, pages + 1):
            article_ids = set()
            list_html = self._get('/real-time/{0}?id=%7B%22db%22%3A%22barronsblog%2Cbarrons%22%2C%22query%22%3A%22language%3Den%20NOT%20(subject-value%3A%3D%27BARBRIEF%27%20or%20subject-value%3A%3D%27BARHIDEFEED%27)%22%2C%22page%22%3A%22{0}%22%2C%22count%22%3A20%7D&type=search_collection'.format(i))
            for match in re.finditer(r'id\\?":\\?"([\w\d]+)\\?"', list_html):
                article_ids.add(match.group(1))
            for id_ in article_ids:
                article_data = self._get('/real-time/{}?id={}&type=article'.format(i, id_))
                url_match = re.search(r'"url\\?":\\?"https:\/\/www.barrons.com(\/articles\/[^"]+)"', article_data)
                article_urls.add(url_match.group(1))

        for url in article_urls:

            article_html = self._get(url)

            headline_match = re.search(r'itemprop="headline">([^<]+)<\/h1>', article_html)
            if not headline_match:
                continue
            headline = clean_html_text(headline_match.group(1))

            date_match = re.search(r'(\w+ \d+, \w+ \d+:\d+ \w+ \w+)\s+<\/time>', article_html)
            if not date_match:
                continue
            date = text_to_datetime(date_match.group(1))

            text = []

            for p_match in re.finditer(r'<p>([\s\S]+?)<\/p>', article_html):
                paragraph = clean_html_text(p_match.group(1))
                if len(paragraph) == 0 or string_contains(paragraph, IGNORE_TEXT):
                    continue
                text.append(paragraph)

            if len(text) == 0:
                continue

            articles.append(Article('barrons', headline, date, '\n\n\n'.join(text), self.url + url))

        return articles

    def read_news(self):
        return self.read_news_list()