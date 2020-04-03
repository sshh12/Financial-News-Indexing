from meta.financialmodelingprep import FinancialModelingPrep
from db import Symbol, Stat
from config import config

import pendulum
import asyncio
import aiohttp


async def fetch_meta_data(name, source):
    try:
        print('[{}] Downloading Meta...'.format(name))
        async with aiohttp.ClientSession() as session:
            source._session = session
            ratings = await source.read_ratings()
            group_stats = await source.read_group_stats()
            n = len(ratings) + len(group_stats)
        print('[{}] Complete, found {}.'.format(name, n))
        return ratings, group_stats
    except ArithmeticError as e:
        print('[{}] Error -> '.format(name), e)
        return []


def daily_rating_to_stat(rating):
    today = pendulum.today()
    updates = [({
        'category': 'Rating',
        'name': 'Trade Rating',
        'source': rating.source,
        'value': rating.scores['overall']['score'],
        'svalue': rating.scores['overall']['recommendation'],
        'found': today,
        'effected': today, 
        'published': today,
        'period': 86400
    }, rating.symbol)]
    return updates


def daily_group_stat_to_stat(gstat):
    today = pendulum.today()
    updates = []
    for sector, change in gstat.groups.items():
        updates.append(({
            'category': 'Sector',
            'name': sector + ' Performance Percent',
            'source': gstat.source,
            'value': change['delta_percent'],
            'svalue': None,
            'found': today,
            'effected': today, 
            'published': today,
            'period': 86400
        }, None))
    return updates


async def main():

    sym_map = {}
    for sym in Symbol.select():
        sym_map[sym.symbol] = sym

    sources = [
        ('FinancialModelingPrep', FinancialModelingPrep(config['meta']['stocks']))
    ]

    stats = []
    tasks = [fetch_meta_data(name, source) for name, source in sources]
    for ratings_data, group_data in await asyncio.gather(*tasks):
        [stats.extend(daily_rating_to_stat(r)) for r in ratings_data]
        [stats.extend(daily_group_stat_to_stat(g)) for g in group_data]

    print('Saving...', len(stats))
    for update, sym in stats:
        if sym is not None and sym in sym_map:
            update['symbol'] = sym_map[sym]
        else:
            update['symbol'] = None
        query = {}
        for key in ['symbol', 'source', 'name', 'effected', 'period']:
            query[key] = update[key]
        st, created = Stat.get_or_create(**query, defaults=update)
        if not created:
            for key, value in update.items():
                setattr(st, key, value)
            st.save()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
