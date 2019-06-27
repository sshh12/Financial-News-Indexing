from articles.reuters import Reuters
from articles.seekingalpha import SeekingAlpha
from articles.marketwatch import MarketWatch
from articles.bloomberg import Bloomberg

import elasticsearch


def main():

    print('Running...')

    articles = []

    try:
        print('Fetching Bloomberg...')
        articles.extend(Bloomberg().read_news())
        print('...done.')
    except Exception as e:
        print('Bloomberg Error', e)

    try:
        print('Fetching MarketWatch...')
        articles.extend(MarketWatch().read_news())
        print('...done.')
    except Exception as e:
        print('MarketWatch Error', e)

    try:
        print('Fetching SeekingAlpha...')
        articles.extend(SeekingAlpha().read_news())
        print('...done.')
    except Exception as e:
        print('SeekingAlpha Error', e)

    try:
        print('Fetching Reuters...')
        articles.extend(Reuters().read_news())
        print('...done.')
    except Exception as e:
        print('Reuters Error', e)

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