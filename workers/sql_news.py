from articles.reuters import Reuters
from articles.seekingalpha import SeekingAlpha
from articles.marketwatch import MarketWatch
from articles.bloomberg import Bloomberg
from articles.barrons import Barrons
from articles.benzinga import Benzinga
from articles.ibtimes import IBTimes
from articles.cnbc import CNBC
from articles.verge import Verge
from articles.cnn import CNN
from articles.thestreet import TheStreet
from articles.businessinsider import BusinessInsider
from articles.yahoo import Yahoo
from articles.washingtonpost import WashingtonPost
from articles.coindesk import CoinDesk
from articles.newspaper3k import Newspaper3k
from articles.twitter import Twitter
from db import db, Symbol, Article
from config import config

import traceback
import asyncio
import aiohttp
import re


SOURCES = {
    'WashingtonPost': WashingtonPost(),
    'Yahoo': Yahoo(),
    'BusinessInsider': BusinessInsider(),
    'TheStreet': TheStreet(),
    'CNN': CNN(),
    'Verge': Verge(),
    'CNBC': CNBC(),
    'IBTimes': IBTimes(),
    'Benzinga': Benzinga(),
    'Barrons': Barrons(),
    'Bloomberg': Bloomberg(),
    'MarketWatch': MarketWatch(),
    'SeekingAlpha': SeekingAlpha(),
    'Reuters': Reuters(),
    'CoinDesk': CoinDesk(),
    'Newspaper3k': Newspaper3k(),
    'Twitter': Twitter()
}


async def fetch_articles(name, source):
    try:
        print('[{}] Downloading...'.format(name))
        async with aiohttp.ClientSession() as session:
            source._session = session
            found = await source.read_news()
        print('[{}] Complete, found {}.'.format(name, len(found)))
        return found
    except Exception as e:
        print('[{}] Error -> '.format(name), e)
        traceback.print_exc()
        return []


def _strip_name(name):
    name = name.replace(' Inc.', '').replace(' & Co.', '').replace('Co.', '')\
        .replace('Corp.', '').replace('Ltd.', '').replace(',', '')\
        .replace(' LP', '')
    name = re.sub(r' \([ \w]+\)', '', name)
    name = re.sub(r' \/[ \w]+\/', '', name)
    name = name.strip()
    name = re.sub(r' Class [A-Z]$', '', name)
    name = re.sub(r' Group$', '', name)
    name = re.sub(r' Holdings$', '', name)
    name = re.sub(r'^The ', '', name)
    return name.strip()


def _str_includes(text, test):
    text = text.replace('GREAT WORK', 'great work')
    return re.search(r'\b' + test + r'\b', text) is not None


def find_obvious_symbols(symbols, article):
    headline, text = article.title, article.content
    comps = set()
    for symbol in symbols:
        sym, name = symbol.symbol, symbol.name
        sym = sym.upper()
        name = _strip_name(name)
        if _str_includes(text, sym) or _str_includes(headline, sym):
            comps.add(symbol)
        elif _str_includes(text, name) or _str_includes(headline, name):
            comps.add(symbol)
    return comps


def article_to_sql_article(article):
    update = {
        'title': article.headline,
        'content': article.content,
        'url': article.url,
        'source': article.source,
        'published': article.date,
        'found': article.found
    }
    return update


async def main():

    symbols = list(Symbol.select())

    updates = []

    fetch_tasks = [fetch_articles(name, SOURCES[name]) for name in config['news']['sources']]
    for source_articles in await asyncio.gather(*fetch_tasks):
        source_articles = [a for a in source_articles if len(a.headline) > 5]
        updates.extend([article_to_sql_article(a) for a in source_articles])

    print('Saving...', len(updates))
    arts = []
    for art_update in updates:
        article, created = Article.get_or_create(url=art_update['url'], defaults=art_update)
        arts.append(article)

    with db.atomic():
        for art in arts:
            symbols = find_obvious_symbols(symbols, art)
            art.symbols.add(list(symbols))
        


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())