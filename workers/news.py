import pymongo
from datetime import datetime
import requests
import time
import os
import re

client = pymongo.MongoClient(os.environ['MONGODB_URI'])
db = client.heroku_f4503299
news = db.news
news.create_index([('key', pymongo.ASCENDING)], unique=True)

class Article:

    def __init__(self, source, headline, date, content, url):
        self.source = source
        self.headline = headline
        self.date = date
        self.content = content
        self.url = url
        self._key = re.sub(r'[^\w\d]', '', self.source + self.headline).lower()
        
    def as_dict(self):
        return {
            'src': self.source,
            'headline': self.headline,
            'date': self.date,
            'content': self.content,
            'url': self.url,
            'key': self._key
        }

def clean_html_text(html):
    html = html.replace('&rsquo;', '\'')
    html = html.replace('&lsquo;', '\'')
    html = html.replace('&ldquo;', '"')
    html = html.replace('&rdquo;', '"')
    html = re.sub(r'&#[\w\d]+;', '', html)
    return html

class Reuters:

    def __init__(self):
        self.url = 'https://www.reuters.com'

    def _get(self, url_part):
        time.sleep(0.2)
        print(self.url + url_part)
        return requests.get(self.url + url_part).text

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
            timestamp = (date_match.group(1) + ' ' + date_match.group(2)).split(' ')
            if len(timestamp[1]) == 2:
                timestamp[1] = '0' + timestamp[1]
            if len(timestamp[3]) == 4:
                timestamp[3] = '0' + timestamp[3]
            date = datetime.strptime(' '.join(timestamp), '%B %d, %Y %I:%M %p')

            headline = headline_match.group(1)

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

print('Running...')
reuters = Reuters()

for rtype in ['businessnews', 'marketsNews', 'technologynews', 'healthnews', 'banks', 'aerospace-defense', 'innovationintellectualproperty', 'environmentnews', 'worldnews']:

    for article in reuters.read_news_list('businessnews'):
        try:
            news.insert_one(article.as_dict())
        except pymongo.errors.DuplicateKeyError:
            pass

print('done.')