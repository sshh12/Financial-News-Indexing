from . import Article, clean_html_text, ArticleScraper
from finnews.config import config

import asyncio
import json


CREDS = config['creds']['stocktwits']


class StockTwits(ArticleScraper):

    def __init__(self):
        self.url = 'https://api.stocktwits.com'

    async def _call_api(self, path):
        headers = {
            'Authorization': 'OAuth ' + CREDS['access_token']
        }
        resp = await self._get('/api/2/' + path, headers=headers)
        try:
            return json.loads(resp)
        except:
            raise Exception('Stocktwits request was blocked.')

    async def read_twits(self):
        data = await self._call_api('streams/suggested.json')
        twits = []
        if data['response']['status'] == 200:
            for twit in data['messages']:
                author = twit['user']['username']
                body = clean_html_text(twit['body'])
                try:
                    sent = twit['entities']['sentiment']['basic']
                except:
                    sent = 'None'
                twits.append((author, body, sent))
        return twits

    async def read_latest_headlines(self):
        headlines = []
        twits = await self.read_twits()
        for author, body, sent in twits:
            text = '{} [{}] -- {}'.format(author, sent, body)
            headlines.append(('http://www.stocktwits.com', '', text))
        return 'stocktwits', headlines
