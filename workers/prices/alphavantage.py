from . import PriceTick, TickDataSource

import pendulum
import asyncio
import json


MAX_REQ_PER_MIN = 5


def _chunks(items, size):
    for i in range(0, len(items), size):
        yield items[i:i + size]


class AlphaVantage(TickDataSource):

    def __init__(self, symbols, api_keys=['demo']):
        self.url = 'https://www.alphavantage.co'
        self.symbols = symbols
        self.api_keys = api_keys

    async def read_stock_data(self, symbol, period=60, key_idx=0, attempt=0):
        
        api_key = self.api_keys[key_idx]
        if period == 60:
            url = '/query?function=TIME_SERIES_INTRADAY&symbol={}&interval=1min&apikey={}'.format(symbol.strip(), api_key)
        else:
            url = '/query?function=TIME_SERIES_DAILY&symbol={}&outputsize=full&apikey={}'.format(symbol.strip(), api_key)

        resp = await self._get(url)
        try:
            res_json = json.loads(resp)
        except:
            print('Oof', resp)
            res_json = None

        if res_json is None or ('Note' in res_json and 'call freq' in res_json['Note']):
            if attempt > 4:
                return []
            else:
                await asyncio.sleep(120)
                return await self.read_stock_data(symbol, attempt=attempt+1)

        if 'Error Message' in res_json or 'Meta Data' not in res_json:
            print(symbol, res_json, url)
            return []

        if period == 60:
            timezone = res_json['Meta Data']['6. Time Zone']
            tick_dict = res_json['Time Series (1min)']
        else:
            timezone = res_json['Meta Data']['5. Time Zone']
            tick_dict = res_json['Time Series (Daily)']

        ticks = []

        for timestamp, data_dict in tick_dict.items():
            if period == 60:
                date = pendulum.from_format(timestamp + ' ' + timezone, 'YYYY-MM-DD HH:mm:ss z')
            else:
                date = pendulum.from_format(timestamp, 'YYYY-MM-DD')
            open_ = data_dict['1. open']
            high = data_dict['2. high']
            low = data_dict['3. low']
            close = data_dict['4. close']
            volume = data_dict['5. volume']
            ticks.append(PriceTick(symbol, 'stock', 'alphavantage', date, open_, high, low, close, volume))

        return ticks

    async def read_ticks(self, period=60):

        ticks = []
        
        first_chunk = True
        for symbols in _chunks(self.symbols, MAX_REQ_PER_MIN * len(self.api_keys)):
            if not first_chunk:
                await asyncio.sleep(61)
            fetch_tasks = [self.read_stock_data(symbol.upper(), key_idx=i % len(self.api_keys), period=period) 
                for i, symbol in enumerate(symbols)]
            for symbol_ticks in await asyncio.gather(*fetch_tasks):
                ticks.extend(symbol_ticks)
            first_chunk = False

        return ticks