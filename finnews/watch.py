from finnews.stream import STREAMS, run_streams
from finnews.utils import config, ensure_dirs
import pendulum
import json
import os


import nest_asyncio

nest_asyncio.apply()


WATCH_DIR = os.path.join(config["data_dir"], "watch")


def filesys_make_on_event(cb=None):

    sym_path = os.path.join(WATCH_DIR, "syms")
    date_path = os.path.join(WATCH_DIR, "date")
    tick_path = os.path.join(WATCH_DIR, "ticks")
    fin_path = os.path.join(WATCH_DIR, "fin")

    ensure_dirs([sym_path, date_path, tick_path, fin_path])

    def on_event(og_evt):
        evt = og_evt.copy()
        date = pendulum.now()
        evt["date"] = str(date)
        evt_json = json.dumps(evt)
        symbols = evt.get("symbols", [])

        def write_evt(fn):
            with open(fn, "a") as f:
                f.write(evt_json + "\n")

        write_evt(os.path.join(date_path, date.isoformat()[:10].replace("-", "_")))
        if cb is not None:
            cb(og_evt)

    return on_event


def watch_all_forever(on_event):
    print("Watching...")
    streams = []
    for stream_name in config["watch"]:
        print(" *", stream_name)
        streams.append(STREAMS[stream_name])
    run_streams(streams, on_event)
