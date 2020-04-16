from prices.alphavantage import AlphaVantage
from prices.cryptocompare import CryptoCompare
from db import Symbol, OHLCV, db
from config import config

import asyncio
import aiohttp


def _chunks(items, size):
    for i in range(0, len(items), size):
        yield items[i:i + size]


async def fetch_tick_data(name, source, **kwargs):
    try:
        print('[{}] Downloading...'.format(name))
        async with aiohttp.ClientSession() as session:
            source._session = session
            found = await source.read_ticks(**kwargs)
        print('[{}] Complete, found {}.'.format(name, len(found)))
        return found
    except ArithmeticError as e:
        print('[{}] Error -> '.format(name), e)
        return []


def tick_to_OHLCV(sym_map, tick, period=60):
    update = {
        'symbol': sym_map[tick.symbol.upper()],
        'open': tick.open,
        'high': tick.high,
        'low': tick.low,
        'close': tick.close,
        'volume': tick.volume,
        'period': period,
        'start': tick.date,
        'end': tick.date.add(seconds=period),
        'source': tick.source
    }
    return update


async def main_minute():

    stock_map = {}
    crypto_map = {}
    for sym in Symbol.select():
        if sym.asset_type == 'stock':
            stock_map[sym.symbol] = sym
        elif sym.asset_type == 'crypto':
            crypto_map[sym.symbol] = sym

    cryptos = list(set(config['prices']['cryptos']) & set(crypto_map))
    stocks = list(set(config['prices']['stocks']) & set(stock_map))

    sources = [
        ('CryptoCompare', CryptoCompare(cryptos)),
        ('AlphaVantage', AlphaVantage(stocks, 
           api_keys=config['creds']['alphavantage']['api_keys']))
    ]

    fetch_tasks = [fetch_tick_data(name, source) for name, source in sources]
    for source_ticks in await asyncio.gather(*fetch_tasks):
        if len(source_ticks) == 0:
            continue
        map_ = (crypto_map if source_ticks[0].type == 'crypto' else stock_map)
        source_ticks = [tick for tick in source_ticks if tick.volume > 0]
        updates = [tick_to_OHLCV(map_, tick) for tick in source_ticks]
        print('Saving...', len(updates))
        db.connect(reuse_if_open=True)
        OHLCV.insert_many(updates).on_conflict('ignore').execute()


async def main_daily():

    stock_map = {}
    for sym in Symbol.select():
        stock_map[sym.symbol] = sym

    stocks = list(set(config['general']['stocks']) & set(stock_map))

    sources = [
        ('AlphaVantage', AlphaVantage(stocks, 
           api_keys=config['creds']['alphavantage']['api_keys']))
    ]

    fetch_tasks = [fetch_tick_data(name, source, period=86400) for name, source in sources]
    for source_ticks in await asyncio.gather(*fetch_tasks):
        if len(source_ticks) == 0:
            continue
        updates = [tick_to_OHLCV(stock_map, tick, period=86400) for tick in source_ticks]
        print('Saving...', len(updates))
        db.connect(reuse_if_open=True)
        OHLCV.insert_many(updates).on_conflict('ignore').execute()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main_daily())
