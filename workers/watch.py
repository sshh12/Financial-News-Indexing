from stream import run_streams
from stream.twitter import StreamTwitter
from stream.tdameritrade import StreamTDA
from stream.prs import StreamPRs
from stream.news import StreamNews
from stream.stats import StreamStats
from stream.guru import StreamGuru
from notify.slack import slack_evt
import json
import hashlib
import pendulum

import nest_asyncio; nest_asyncio.apply()


def _hash(s):
    return hashlib.sha1(bytes(repr(s), 'utf-8')).hexdigest()


def stdio_make_on_event(cb=None):
    def on_event(og_evt):
        evt = og_evt.copy()
        evt['date'] = str(pendulum.now())
        if 'guru-' not in evt.get('name', ''):
            print(evt)
        if cb is not None:
            cb(og_evt)
    return on_event


def es_make_on_event(cb=None):
    import elasticsearch
    es = elasticsearch.Elasticsearch()
    def on_event(og_evt):
        evt = og_evt.copy()
        id_ = _hash(evt)
        evt['date'] = str(pendulum.now())
        index = 'index-events'
        if 'guru-' not in evt.get('name', ''):
            try:
                es.create(index=index, id=id_, body=evt, doc_type='event')
            except Exception as e:
                pass
        if cb is not None:
            cb(og_evt)
    return on_event


def io_make_on_event():
    import os
    sym_path = os.path.join('data', 'watch', 'syms')
    type_path = os.path.join('data', 'watch', 'type')
    date_path = os.path.join('data', 'watch', 'date')
    tick_path = os.path.join('data', 'watch', 'ticks')
    def mkdir(path):
        try:
            os.makedirs(path)
        except:
            pass
    mkdir(sym_path)
    mkdir(type_path)
    mkdir(date_path)
    mkdir(tick_path)
    def on_event(evt):
        evt = evt.copy()
        evt_json = json.dumps(evt)
        symbols = evt.get('symbols', [])
        if 'guru-' not in evt.get('name', ''):
            type_ = '_'.join([str(k) for k in sorted(evt)][:10])
        else:
            type_ = 'guru_all'
        if evt.get('type') == 'error':
            type_ = 'error'
        date = pendulum.now()
        evt['date'] = str(date)
        def write_evt(fn):
            with open(fn, 'a') as f:
                f.write(evt_json + '\n')
        write_evt(os.path.join(type_path, type_))
        write_evt(os.path.join(date_path, date.isoformat()[:10].replace('-', '_')))
        if len(symbols) == 0:
            write_evt(os.path.join(sym_path, '_NO_SYM'))
        else:
            for symbol in symbols:
                write_evt(os.path.join(sym_path, symbol))
    return on_event


def main():

    io_logger = io_make_on_event()
    on_event = stdio_make_on_event(cb=io_logger)

    print('Streaming...')

    run_streams([
        StreamTDA,
        StreamTwitter,
        StreamTDA,
        StreamPRs,
        StreamStats,
        StreamNews,
        StreamGuru
    ], on_event)


if __name__ == '__main__':
    main()