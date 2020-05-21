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


def _hash(s):
    return hashlib.sha1(bytes(repr(s), 'utf-8')).hexdigest()


def stdio_make_on_event(evt):
    def on_event(evt):
        evt['date'] = str(pendulum.now())
        print(evt)


def es_make_on_event(cb=None):
    import elasticsearch
    es = elasticsearch.Elasticsearch()
    def on_event(og_evt):
        evt = og_evt.copy()
        id_ = _hash(evt)
        evt['date'] = str(pendulum.now())
        index = 'index-events'
        if 'guru-' in evt.get('name', ''):
            index = 'index-' + evt['name']
        try:
            es.create(index=index, id=id_, body=evt, doc_type='event')
            if cb is not None:
                cb(og_evt)
        except Exception as e:
            pass
    return on_event


def io_make_on_event():
    import os
    sym_path = os.path.join('data', 'watch', 'syms')
    type_path = os.path.join('data', 'watch', 'type')
    date_path = os.path.join('data', 'watch', 'date')
    def mkdir(path):
        try:
            os.makedirs(path)
        except:
            pass
    mkdir(sym_path)
    mkdir(type_path)
    mkdir(date_path)
    def on_event(evt):
        evt = evt.copy()
        type_ = _hash(list(evt.keys()))
        date = pendulum.now()
        evt['date'] = str(date)
        with open(os.path.join(type_path, type_), 'a') as f:
            f.write(str(evt) + '\n')
        with open(os.path.join(date_path, date.isoformat()[:10].replace('-', '_')), 'a') as f:
            f.write(str(evt) + '\n')
        for symbol in evt.get('symbols', []):
            with open(os.path.join(sym_path, symbol), 'a') as f:
                f.write(str(evt) + '\n')


def main():

    a = io_make_on_event()
    on_event = es_make_on_event(cb=a)

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