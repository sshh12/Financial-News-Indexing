from articles.reuters import Reuters
from articles.seekingalpha import SeekingAlpha
from articles.marketwatch import MarketWatch
from articles.bloomberg import Bloomberg
from articles.barrons import Barrons
from articles.benzinga import Benzinga
from articles.ibtimes import IBTimes
from articles.cnbc import CNBC

import elasticsearch


def main():

    print('Running...')

    articles = []

    sources = [
        ('CNBC', CNBC()),
        ('IBTimes', IBTimes()),
        ('Benzinga', Benzinga()),
        ('Barrons', Barrons()),
        ('Bloomberg', Bloomberg()),
        ('MarketWatch', MarketWatch()),
        ('SeekingAlpha', SeekingAlpha()),
        ('Reuters', Reuters())
    ]

    for name, source in sources:
        try:
            print('Fetching {}...'.format(name))
            found = source.read_news()
            articles.extend(found)
            print('...found {}, done.'.format(len(found)))
        except Exception as e:
            print('{} Error'.format(name), e)

    print('Saving {} articles...'.format(len(articles)))
    es = elasticsearch.Elasticsearch()
    for article in articles:
        try:
            es.create('index-news', article._id, article.as_dict())
        except elasticsearch.exceptions.ConflictError:
            pass
    print('...done.')


if __name__ == "__main__":
    main()