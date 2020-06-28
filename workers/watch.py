from stream import run_streams
from stream.twitter import StreamTwitter
from stream.tdameritrade import StreamTDA
from stream.prs import StreamPRs
from stream.news import StreamNews
from stream.stats import StreamStats
from stream.guru import StreamGuru
from notify.slack import slack_evt
from config import config
import json
import hashlib
import pendulum

import nest_asyncio

nest_asyncio.apply()


def _hash(s):
    return hashlib.sha1(bytes(repr(s), "utf-8")).hexdigest()


def _get_channels(evt):
    if evt.get("type") == "error":
        type_ = "_error"
    else:
        type_ = "_".join([str(k) for k in sorted(evt)][:10])
    channels = ["*", type_]
    symbols = evt.get("symbols", [])
    if len(symbols) == 0:
        channels.append("_NONE")
    else:
        channels.extend(symbols)
    return channels


def stdio_make_on_event(cb=None):
    def on_event(og_evt):
        evt = og_evt.copy()
        evt["date"] = str(pendulum.now())
        if evt.get("type") == "error":
            print(evt)
        else:
            print(evt.get("symbols", []))
        if cb is not None:
            cb(og_evt)

    return on_event


def es_make_on_event(cb=None):
    import elasticsearch

    es = elasticsearch.Elasticsearch()

    def on_event(og_evt):
        evt = og_evt.copy()
        id_ = _hash(evt)
        evt["date"] = str(pendulum.now())
        index = "index-events"
        if "guru-" not in evt.get("name", ""):
            try:
                es.create(index=index, id=id_, body=evt, doc_type="event")
            except Exception as e:
                pass
        if cb is not None:
            cb(og_evt)

    return on_event


def redis_make_event(cb=None):
    import redis

    redis_cfg = config["creds"]["redis"]
    rs = redis.Redis(host=redis_cfg["host"], password=redis_cfg["password"], port=redis_cfg["port"])

    def on_event(og_evt):
        evt = og_evt.copy()
        evt["ts"] = pendulum.now().timestamp()
        evt_json = json.dumps(evt)
        rs.publish("*", evt_json)
        if cb is not None:
            cb(og_evt)

    return on_event


def io_make_on_event(cb=None):
    import os

    sym_path = os.path.join("data", "watch", "syms")
    type_path = os.path.join("data", "watch", "type")
    date_path = os.path.join("data", "watch", "date")
    tick_path = os.path.join("data", "watch", "ticks")
    fin_path = os.path.join("data", "watch", "fin")

    def mkdir(path):
        try:
            os.makedirs(path)
        except:
            pass

    for path in [sym_path, type_path, date_path, tick_path, fin_path]:
        mkdir(path)

    def on_event(og_evt):
        evt = og_evt.copy()
        evt["date"] = str(pendulum.now())
        evt_json = json.dumps(evt)
        symbols = evt.get("symbols", [])
        if evt.get("type") == "error":
            type_ = "_error"
        else:
            type_ = "_".join([str(k) for k in sorted(evt)][:10])
        date = pendulum.now()
        evt["date"] = str(date)

        def write_evt(fn):
            with open(fn, "a") as f:
                f.write(evt_json + "\n")

        write_evt(os.path.join(type_path, type_))
        write_evt(os.path.join(date_path, date.isoformat()[:10].replace("-", "_")))
        if len(symbols) == 0:
            write_evt(os.path.join(sym_path, "_NONE"))
        else:
            for symbol in symbols:
                write_evt(os.path.join(sym_path, symbol))
        if cb is not None:
            cb(og_evt)

    return on_event


def main():

    cb_io = io_make_on_event()
    on_event = stdio_make_on_event(cb=cb_io)

    print("Streaming...")

    run_streams([StreamTDA, StreamTwitter, StreamPRs, StreamStats, StreamNews, StreamGuru], on_event)


if __name__ == "__main__":
    main()
