from articles.reuters import Reuters
from articles.seekingalpha import SeekingAlpha

import elasticsearch


def main():

    print('Running...')

    articles = []

    try:
        print('Fetching SeekingAlpha...', end='')
        articles.extend(SeekingAlpha().read_news())
        print('done.')
    except Exception as e:
        print('SeekingAlpha Error', e)

    try:
        print('Fetching Reuters...', end='')
        articles.extend(Reuters().read_news())
        print('done.')
    except Exception as e:
        print('Reuters Error', e)

    print('Saving...', end='')
    es = elasticsearch.Elasticsearch()
    for article in articles:
        try:
            es.create('index-news', article._id, article.as_dict())
        except elasticsearch.exceptions.ConflictError:
            pass
    print('done.')


if __name__ == "__main__":
    main()