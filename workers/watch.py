from stream.twitter import StreamTwitter
from stream.tdameritrade import StreamTDA
from stream.prs import StreamPRs
from stream.news import StreamNews
from stream.stats import StreamStats
from stream.guru import StreamGuru
from notify.slack import slack_evt
import hashlib
import pendulum

import nest_asyncio; nest_asyncio.apply()


def on_event(evt):
    evt['date'] = str(pendulum.now())
    print(evt)


def es_make_on_event():
    import elasticsearch
    es = elasticsearch.Elasticsearch()
    def on_event(evt):
        id_ = hashlib.sha1(bytes(repr(evt), 'utf-8')).hexdigest()
        evt['date'] = str(pendulum.now())
        index = 'index-events'
        if 'guru-' in evt.get('name', ''):
            index = 'index-' + evt['name']
        try:
            es.create(index=index, id=id_, body=evt, doc_type='event')
        except Exception as e:
            pass
    return on_event


def main():

    print('Watching...')
    
    strm_twitter = StreamTwitter()
    strm_twitter.on_event = on_event
    strm_twitter.start_async()

    strm_tda = StreamTDA()
    strm_tda.on_event = on_event
    strm_tda.start_async()

    strm_prs = StreamPRs()
    strm_prs.on_event = on_event
    strm_prs.start_async()

    strm_stats = StreamStats()
    strm_stats.on_event = on_event
    strm_stats.start_async()

    strm_news = StreamNews()
    strm_news.on_event = on_event
    strm_news.start_async()

    strm_guru = StreamGuru()
    strm_guru.on_event = on_event
    strm_guru.start()


if __name__ == '__main__':
    main()