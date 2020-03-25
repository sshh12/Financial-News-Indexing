from . import Article, clean_html_text, ArticleScraper, string_contains, text_to_datetime, truncate_sentence
import pendulum

import twitter
import asyncio
import re
from config import config


USERS = config['news']['twitter']['users']
TW_CREDS = config['creds']['twitter']
API = twitter.Api(
    consumer_key=TW_CREDS['consumer_key'],
    consumer_secret=TW_CREDS['consumer_secret'],
    access_token_key=TW_CREDS['access_token_key'],
    access_token_secret=TW_CREDS['access_token_secret']
)


class Twitter(ArticleScraper):

    def __init__(self):
        pass

    def read_status_by_user(self, user, count=100):
        try:
            return API.GetUserTimeline(screen_name=user, include_rts=True, count=count)
        except Exception as e:
            print('Twitter', user, e)
            return []

    def status_to_article(self, status):
        user = status.user
        cleaned = clean_html_text(status.text)
        if len(cleaned) < 10:
            return None
        trucated = truncate_sentence(cleaned)
        text = '{} (@{}) - {}'.format(user.name, user.screen_name, cleaned)
        headline = user.name + ' - ' + trucated
        url = 'https://twitter.com/{}/status/{}'.format(user.screen_name, status.id)
        date = text_to_datetime(status.created_at)
        return Article('twitter', headline, date, text, url)

    async def read_news(self):
        all_articles = []
        for user in USERS:
            all_articles.extend([self.status_to_article(status) 
                for status in self.read_status_by_user(user)])
        return [a for a in all_articles if a is not None]