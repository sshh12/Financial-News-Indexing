from . import Article
from finnews.articles.abs import ArticleScraper
from finnews.articles.utils import clean_html_text, text_to_datetime, string_contains, truncate_sentence

import twitter
import asyncio
import re
from finnews.config import config


USERS = config["news"]["twitter"]["users"]
TW_CREDS = config["creds"]["twitter"]
API = twitter.Api(
    consumer_key=TW_CREDS["consumer_key"],
    consumer_secret=TW_CREDS["consumer_secret"],
    access_token_key=TW_CREDS["access_token_key"],
    access_token_secret=TW_CREDS["access_token_secret"],
    tweet_mode="extended",
)


class Twitter(ArticleScraper):
    def __init__(self):
        pass

    def read_status_by_user(self, user, count=100):
        try:
            return API.GetUserTimeline(screen_name=user, include_rts=True, count=count)
        except Exception as e:
            print("Twitter", user, e)
            return []

    def status_to_article(self, status):
        user = status.user
        try:
            cleaned = clean_html_text(status.full_text)
            assert len(cleaned) > 10
        except Exception as e:
            return None
        trucated = truncate_sentence(cleaned)
        headline = user.name + " - " + trucated
        url = "https://twitter.com/{}/status/{}".format(user.screen_name, status.id)
        date = text_to_datetime(status.created_at)
        return Article("twitter", headline, date, cleaned, url)

    async def read_news(self):
        all_articles = []
        for user in USERS:
            all_articles.extend([self.status_to_article(status) for status in self.read_status_by_user(user)])
        return [a for a in all_articles if a is not None]
