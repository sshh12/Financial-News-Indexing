from meta.financialmodelingprep import FinancialModelingPrep
from config import config

import elasticsearch
import asyncio
import aiohttp


async def fetch_rating_data(name, source):
    try:
        print('[{}] Downloading Ratings...'.format(name))
        async with aiohttp.ClientSession() as session:
            source._session = session
            found = await source.read_ratings()
        print('[{}] Complete, found {}.'.format(name, len(found)))
        return found
    except ArithmeticError as e:
        print('[{}] Error -> '.format(name), e)
        return []


async def main():

    sources = [
        ('FinancialModelingPrep', FinancialModelingPrep(config['meta']['stocks']))
    ]

    ratings = []
    tasks = [fetch_rating_data(name, source) for name, source in sources]
    for source_data in await asyncio.gather(*tasks):
        ratings.extend(source_data)

    print('[ElasticSearch] Saving {} meta ratings...'.format(len(ratings)))
    cnt = 0
    es = elasticsearch.Elasticsearch()
    for rating in ratings:
        try:
            es.create('index-rating', rating._id, rating.as_dict())
            cnt += 1
        except elasticsearch.exceptions.ConflictError:
            pass
    print('[ElasticSearch] Saved {}.'.format(cnt))


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
