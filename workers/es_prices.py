from prices.alphavantage import AlphaVantage
from prices.cryptocompare import CryptoCompare
from config import config

import elasticsearch
import asyncio
import aiohttp


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
        ('CryptoCompare', CryptoCompare(config['prices']['cryptos'])),
        ('AlphaVantage', AlphaVantage(config['prices']['stocks'], 
            api_key=config['creds']['alphavantage']['api_key']))
    ]

    ticks = []

    fetch_tasks = [fetch_tick_data(name, source) for name, source in sources]
    for source_ticks in await asyncio.gather(*fetch_tasks):
        ticks.extend(source_ticks)

    print('[ElasticSearch] Saving {} ticks...'.format(len(ticks)))
    cnt = 0
    es = elasticsearch.Elasticsearch()
    for tick in ticks:
        try:
            es.create('index-ticks', tick._id, tick.as_dict())
            cnt += 1
        except elasticsearch.exceptions.ConflictError:
            pass
    print('[ElasticSearch] Saved {}.'.format(cnt))


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
