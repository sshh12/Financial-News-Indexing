from . import TradeRating, MetaDataSource

import asyncio
import json


class FinancialModelingPrep(MetaDataSource):

    def __init__(self, symbols):
        self.url = 'https://financialmodelingprep.com'
        self.symbols = symbols

    async def _call_api(self, path):
        data = await self._get('/api/v3/{}'.format(path))
        return json.loads(data)

    async def read_rating(self, symbol):
        resp = await self._call_api('company/rating/{}'.format(symbol))
        if 'rating' not in resp:
            return None
        scores = {'overall': resp['rating']}
        for name in resp['ratingDetails']:
            scores[name] = resp['ratingDetails'][name]
        return TradeRating(symbol, 'fmp', scores)

    async def read_ratings(self):
        ratings = []
        fetch_tasks = [self.read_rating(symbol.upper()) for symbol in self.symbols]
        for symbol_rating in await asyncio.gather(*fetch_tasks):
            if symbol_rating is not None:
                ratings.append(symbol_rating)
        return ratings