from . import Article, clean_html_text, HEADERS, string_contains, text_to_datetime

import requests
import time
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


class CNBC:

    def __init__(self):
        self.url = 'https://www.cnbc.com'

    def _get(self, url_part):
        time.sleep(0.2)
        return requests.get(self.url + url_part, headers=HEADERS).text

    def read_news_list(self, topic_urls):

        articles = []
        
        article_urls = set()
        for url in topic_urls:
            list_html = self._get(url)
            for match in re.finditer(r'href=\'(\/\d{4}[^\']+)\'', list_html):
                article_urls.add(match.group(1))

        for url in article_urls:

            article_html = self._get(url)
            
            headline_match = re.search(r'ArticleHeader-headline">([^<]+)<\/h1>', article_html)
            if not headline_match:
                continue
            headline = clean_html_text(headline_match.group(1))

            full_date_match = re.search(r'Published \w+, (\w+ \d+ \d+) <span class="ArticleHeader-datetimeDivider"><\/span> (\d+:\d+ \w+ \w+)<\/time>', article_html)
            rel_date_match = re.search(r'published-timestamp">Published (\d hours ago)<\/time>', article_html)
            if full_date_match:
                date = text_to_datetime(full_date_match.group(1) + ' ' + full_date_match.group(2))
            elif rel_date_match:
                date = text_to_datetime(rel_date_match.group(1))
            else:
                continue

            text = []

            for p_match in re.finditer(r'<p>([\s\S]+?)<\/p>', article_html):
                paragraph = clean_html_text(p_match.group(1))
                if paragraph.count(' ') <= 1 or string_contains(paragraph, IGNORE_TEXT):
                    continue
                text.append(paragraph)

            if len(text) == 0:
                continue

            articles.append(Article('cnbc', headline, date, '\n\n\n'.join(text), self.url + url))

        return articles

    def read_news(self):
        return self.read_news_list(TOPIC_URLS)