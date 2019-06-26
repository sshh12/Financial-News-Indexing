from articles.reuters import Reuters

import elasticsearch


def main():

    print('Running...')

    articles = []

    try:
        print('Fetching Reuters...', end='')
        reuters = Reuters()
        articles.extend(reuters.read_news())
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