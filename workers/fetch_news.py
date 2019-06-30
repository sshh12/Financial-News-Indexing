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

import elasticsearch
import asyncio
import aiohttp


async def fetch_articles(name, source):
    try:
        print('[{}] Downloading...'.format(name))
        async with aiohttp.ClientSession() as session:
            source._session = session
            found = await source.read_news()
        print('[{}] Complete, found {}.'.format(name, len(found)))
        return found
    except ArithmeticError as e:
        print('[{}] Error -> '.format(name), e)
        return []


async def main():

    sources = [
        ('Yahoo', Yahoo()),
        ('BusinessInsider', BusinessInsider()),
        ('TheStreet', TheStreet()),
        ('CNN', CNN()),
        ('Verge', Verge()),
        ('CNBC', CNBC()),
        ('IBTimes', IBTimes()),
        ('Benzinga', Benzinga()),
        ('Barrons', Barrons()),
        ('Bloomberg', Bloomberg()),
        ('MarketWatch', MarketWatch()),
        ('SeekingAlpha', SeekingAlpha()),
        ('Reuters', Reuters())
    ]

    articles = []

    fetch_tasks = [fetch_articles(name, source) for name, source in sources]
    for source_articles in await asyncio.gather(*fetch_tasks):
        articles.extend(source_articles)

    print('[ElasticSearch] Saving {} articles...'.format(len(articles)))
    es = elasticsearch.Elasticsearch()
    cnt = 0
    for article in articles:
        try:
            es.create('index-news', article._id, article.as_dict())
            cnt += 1
        except elasticsearch.exceptions.ConflictError:
            pass
    print('[ElasticSearch] Saved {}.'.format(cnt))


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())