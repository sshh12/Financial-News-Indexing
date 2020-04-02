from meta.financialmodelingprep import FinancialModelingPrep
from db import Symbol
from config import config

import asyncio
import aiohttp


async def main():

    for crypto_sym in config['prices']['cryptos']:
        symbol = Symbol(symbol=crypto_sym, name=crypto_sym, asset_type='crypto')
        try:
            symbol.save(force_insert=True)
        except:
            print(crypto_sym, 'already exists.')
    
    async with aiohttp.ClientSession() as session:

        fmp = FinancialModelingPrep()
        fmp._session = session

        stock_symbols = config['prices']['stocks'] + config['meta']['stocks']
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
            symbol = Symbol(symbol=sym, name=name, desc=desc, industry=industry, sector=sector, asset_type='stock')
            try:
                symbol.save(force_insert=True)
            except:
                print(sym, 'already exists.')


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
