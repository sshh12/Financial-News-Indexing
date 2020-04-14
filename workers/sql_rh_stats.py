from tradinhood import Robinhood
from db import Symbol, Stat
from config import config

import pendulum
import asyncio
import aiohttp


RH_CREDS = config['creds']['robinhood']


def _chunks(items, size):
    for i in range(0, len(items), size):
        yield items[i:i + size]


def rh_pop_to_stat(symbol, pop):
    now = pendulum.now()
    if pop is None:
        return []
    updates = [({
        'category': 'Robinhood',
        'name': 'Robinhood Popularity',
        'source': 'robinhood',
        'value': pop,
        'svalue': None,
        'found': now,
        'effected': now, 
        'published': now,
        'period': 0
    }, symbol)]
    return updates


def rh_rating_to_stat(symbol, rating):
    now = pendulum.now()
    if rating is None:
        return []
    br = rating['num_buy_ratings']
    hr = rating['num_hold_ratings']
    sr = rating['num_sell_ratings']
    updates = [({
        'category': 'Robinhood',
        'name': 'Robinhood Buy Rating',
        'source': 'robinhood',
        'value': br / (br + hr + sr),
        'svalue': None,
        'found': now,
        'effected': now, 
        'published': now,
        'period': 0
    }, symbol), ({
        'category': 'Robinhood',
        'name': 'Robinhood Sell Rating',
        'source': 'robinhood',
        'value': sr / (br + hr + sr),
        'svalue': None,
        'found': now,
        'effected': now, 
        'published': now,
        'period': 0
    }, symbol)]
    return updates


async def main():

    sym_map = {}
    for sym in Symbol.select():
        sym_map[sym.symbol] = sym

    symbols = list(set(config['general']['stocks']) & set(sym_map))

    rbh = Robinhood()
    try:
        rbh.load_login('data/rh.login')
        _ = rbh.cash
    except Exception as e:
        print(e)
        rbh.login(username=RH_CREDS['username'], password=RH_CREDS['password'])
        rbh.save_login('data/rh.login')

    rh_symbols = []
    for sym in symbols:
        try:
            rh_symbols.append(rbh[sym])
        except:
            pass
    
    stats = []
    for chunk in _chunks(rh_symbols, 50):
        popularity = rbh.get_bulk_popularity(chunk)
        for symbol, pop in popularity.items():
            stats.extend(rh_pop_to_stat(sym_map[symbol.symbol], pop))
        ratings = rbh.get_bulk_ratings(chunk)
        for symbol, rating in ratings.items():
            stats.extend(rh_rating_to_stat(sym_map[symbol.symbol], rating))

    print('Saving...', len(stats))
    Stat.insert_many(stats).on_conflict('ignore').execute()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
