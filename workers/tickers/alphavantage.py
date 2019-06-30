from . import PriceTick, TickDataSource

import pendulum
import asyncio
import json


MAX_REQ_PER_MIN = 5


def _chunks(items, size):
    for i in range(0, len(items), size):
        yield items[i:i + size]


class AlphaVantage(TickDataSource):

    def __init__(self, symbols, api_key='demo'):
        self.url = 'https://www.alphavantage.co'
        self.symbols = symbols
        self.api_key = api_key

    async def read_stock_data(self, symbol, ignore_note=False):
        
        res_json = json.loads(await self._get('/query?function=TIME_SERIES_INTRADAY&symbol={}&interval=1min&apikey={}'.format(symbol, self.api_key)))

        if not ignore_note and 'Note' in res_json and 'call freq' in res_json['Note']:
            await asyncio.sleep(60)
            return await self.read_stock_data(symbol, ignore_note=True)

        timezone = res_json['Meta Data']['6. Time Zone']
        tick_dict = res_json['Time Series (1min)']

        ticks = []

        for timestamp, data_dict in tick_dict.items():
            date = pendulum.from_format(timestamp + ' ' + timezone, 'YYYY-MM-DD HH:mm:ss z')
            open_ = data_dict['1. open']
            high = data_dict['2. high']
            low = data_dict['3. low']
            close = data_dict['4. close']
            volume = data_dict['5. volume']
            ticks.append(PriceTick(symbol, 'stock', 'alphavantage', date, open_, high, low, close, volume))

        return ticks

    async def read_ticks(self):

        ticks = []
        
        for symbols in _chunks(self.symbols, MAX_REQ_PER_MIN):
            fetch_tasks = [self.read_stock_data(symbol.upper()) for symbol in symbols]
            for symbol_ticks in await asyncio.gather(*fetch_tasks):
                ticks.extend(symbol_ticks)
            await asyncio.sleep(60)

        return ticks