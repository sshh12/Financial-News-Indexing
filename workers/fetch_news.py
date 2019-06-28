from articles.reuters import Reuters
from articles.seekingalpha import SeekingAlpha
from articles.marketwatch import MarketWatch
from articles.bloomberg import Bloomberg
from articles.barrons import Barrons

import elasticsearch


def main():

    print('Running...')

    articles = []

    sources = [
        ('Barrons', Barrons()),
        ('Bloomberg', Bloomberg()),
        ('MarketWatch', MarketWatch()),
        ('SeekingAlpha', SeekingAlpha()),
        ('Reuters', Reuters())
    ]

    for name, source in sources:
        try:
            print('Fetching {}...'.format(name))
            articles.extend(source.read_news())
            print('...done.')
        except Exception as e:
            print('{} Error'.format(name), e)

    print('Saving...')
    es = elasticsearch.Elasticsearch()
    for article in articles:
        try:
            es.create('index-news', article._id, article.as_dict())
        except elasticsearch.exceptions.ConflictError:
            pass
    print('...done.')


if __name__ == "__main__":
    main()