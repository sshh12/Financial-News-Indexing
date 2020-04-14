from prices.alphavantage import AlphaVantage
from prices.cryptocompare import CryptoCompare
from db import Symbol, OHLCV
from config import config

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


def tick_to_OHLCV(sym_map, tick):
    update = {
        'symbol': sym_map[tick.symbol.upper()],
        'open': tick.open,
        'high': tick.high,
        'low': tick.low,
        'close': tick.close,
        'volume': tick.volume,
        'period': 60,
        'start': tick.date,
        'end': tick.date.add(minutes=1),
        'source': tick.source
    }
    return update


async def main():

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

    updates = []

    fetch_tasks = [fetch_tick_data(name, source) for name, source in sources]
    for source_ticks in await asyncio.gather(*fetch_tasks):
        if len(source_ticks) == 0:
            continue
        map_ = (crypto_map if source_ticks[0].type == 'crypto' else stock_map)
        source_ticks = [tick for tick in source_ticks if tick.volume > 0]
        updates.extend([tick_to_OHLCV(map_, tick) for tick in source_ticks])

    print('Saving...', len(updates))
    OHLCV.insert_many(updates).on_conflict('ignore').execute()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
