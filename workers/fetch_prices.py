from tickers.alphavantage import AlphaVantage
from tickers.cryptocompare import CryptoCompare

import elasticsearch
import asyncio
import aiohttp


STOCKS = [
    'MSFT'
]

CRYPTOS = [
    'BTC'
]


async def fetch_tick_data(name, source):
    try:
        print('[{}] Downloading...'.format(name))
        async with aiohttp.ClientSession() as session:
            source._session = session
            found = await source.read_ticks()
        print('[{}] Complete, found {}.'.format(name, len(found)))
        return found
    except ArithmeticError as e:
        print('[{}] Error -> '.format(name), e)
        return []


async def main():

    sources = [
        ('CryptoCompare', CryptoCompare(CRYPTOS)),
        ('AlphaVantage', AlphaVantage(STOCKS, api_key='MCGHKC5Z4IEPGT8V'))
    ]

    ticks = []

    fetch_tasks = [fetch_tick_data(name, source) for name, source in sources]
    for source_ticks in await asyncio.gather(*fetch_tasks):
        ticks.extend(source_ticks)

    print('Saving {} ticks...'.format(len(ticks)))
    es = elasticsearch.Elasticsearch()
    for tick in ticks:
        try:
            es.create('index-ticks', tick._id, tick.as_dict())
        except elasticsearch.exceptions.ConflictError:
            pass
    print('...done.')


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())