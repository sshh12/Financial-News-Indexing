from meta.financialmodelingprep import FinancialModelingPrep
from config import config

import elasticsearch
import asyncio
import aiohttp


async def fetch_meta_data(name, source):
    try:
        print('[{}] Downloading Meta...'.format(name))
        async with aiohttp.ClientSession() as session:
            source._session = session
            ratings = await source.read_ratings()
            lists = await source.read_lists()
            group_stats = await source.read_group_stats()
            n = len(ratings) + len(lists) + len(group_stats)
        print('[{}] Complete, found {}.'.format(name, n))
        return ratings, lists, group_stats
    except ArithmeticError as e:
        print('[{}] Error -> '.format(name), e)
        return []


async def main():

    sources = [
        ('FinancialModelingPrep', FinancialModelingPrep(config['meta']['stocks']))
    ]

    ratings = []
    lists = []
    group_stats = []
    tasks = [fetch_meta_data(name, source) for name, source in sources]
    for ratings_data, list_data, group_data in await asyncio.gather(*tasks):
        ratings.extend(ratings_data)
        lists.extend(list_data)
        group_stats.extend(group_data)

    print('[ElasticSearch] Saving {} meta...'.format(len(ratings)))
    cnt = 0
    es = elasticsearch.Elasticsearch()
    indexes = [
        ('index-rating', ratings),
        ('index-symb-list', lists),
        ('index-group-stats', group_stats)
    ]
    for index, data in indexes:
        for item in data:
            try:
                es.create(index, item._id, item.as_dict())
                cnt += 1
            except elasticsearch.exceptions.ConflictError:
                pass
    print('[ElasticSearch] Saved {}.'.format(cnt))


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
