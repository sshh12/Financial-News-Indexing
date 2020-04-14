from stats.financialmodelingprep import FinancialModelingPrep
from config import config
from db import Symbol

import asyncio
import aiohttp


async def main():

    updates = []

    for crypto_sym in config['general']['cryptos']:
        updates.append(dict(symbol=crypto_sym, name=crypto_sym, industry=None, sector=None, asset_type='crypto'))
    
    async with aiohttp.ClientSession() as session:

        fmp = FinancialModelingPrep()
        fmp._session = session

        stock_symbols = config['prices']['stocks'] + config['stats']['stocks'] + config['general']['stocks']
        stock_symbols = list(set(stock_symbols))

        fetch_tasks = [fmp._call_api('company/profile/' + sym) for sym in stock_symbols]
        for sym_info in await asyncio.gather(*fetch_tasks):
            if 'symbol' not in sym_info:
                print(sym_info)
                continue
            sym = sym_info['symbol']
            name = sym_info['profile']['companyName']
            desc = sym_info['profile']['description']
            industry = sym_info['profile']['industry']
            sector = sym_info['profile']['sector']
            updates.append(dict(symbol=sym, name=name, desc=desc, industry=industry, sector=sector, asset_type='stock'))

    print('Saving...', len(updates))
    Symbol.insert_many(updates).on_conflict('ignore').execute()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
