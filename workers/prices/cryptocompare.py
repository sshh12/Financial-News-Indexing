from . import PriceTick, TickDataSource

import pendulum
import asyncio
import json


class CryptoCompare(TickDataSource):

    def __init__(self, symbols):
        self.url = 'https://min-api.cryptocompare.com'
        self.symbols = symbols

    async def read_crypto_data(self, symbol):
        
        res_json = json.loads(await self._get('/data/histominute?fsym={}&tsym=USD'.format(symbol)))

        ticks = []

        for data_dict in res_json['Data']:
            date = pendulum.from_format(str(data_dict['time']), 'X')
            open_ = data_dict['open']
            high = data_dict['high']
            low = data_dict['low']
            close = data_dict['close']
            volume = data_dict['volumeto']
            ticks.append(PriceTick(symbol, 'crypto', 'cryptocompare', date, open_, high, low, close, volume))

        return ticks

    async def read_ticks(self):

        ticks = []

        fetch_tasks = [self.read_crypto_data(symbol.upper()) for symbol in self.symbols]
        for symbol_ticks in await asyncio.gather(*fetch_tasks):
            ticks.extend(symbol_ticks)

        return ticks