from . import Article, clean_html_text, HEADERS, text_to_datetime

import requests
import time
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


class Reuters:

    def __init__(self):
        self.url = 'https://www.reuters.com'

    def _get(self, url_part):
        time.sleep(0.2)
        return requests.get(self.url + url_part, headers=HEADERS).text

    def read_news_list(self, topic):

        articles = []
        
        article_urls = set()
        list_html = self._get('/news/archive/{}?view=page&page=1&pageSize=10'.format(topic))
        for match in re.finditer(r'href="(\/article\/[^"]+)"', list_html):
            article_urls.add(match.group(1))

        for url in article_urls:

            article_html = self._get(url)

            date_match = re.search(r'(\w+ \d+, \d{4}) \/\s+(\d+:\d+ \w+) ', article_html)
            headline_match = re.search(r'ArticleHeader_headline">([^<]+)<\/h1>', article_html)
            date = text_to_datetime(date_match.group(1) + ' ' + date_match.group(2))

            headline = clean_html_text(headline_match.group(1))

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
                continue

            articles.append(Article('reuters', headline, date, '\n\n\n'.join(text), self.url + url))

        return articles

    def read_news(self):

        all_articles = []
        for topic in TOPIC_URLS:
            all_articles.extend(self.read_news_list(topic))

        return all_articles