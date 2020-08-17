from finnews.stream import STREAMS, run_streams
from finnews.utils import config, ensure_dirs
import pendulum
import json
import os


import nest_asyncio

nest_asyncio.apply()


WATCH_DIR = os.path.join(config["data_dir"], "watch")


def watch_all_forever(on_event):
    print("Watching...")
    streams = []
    for stream_name in config["watch"]:
        print(" *", stream_name)
        streams.append(STREAMS[stream_name])
    run_streams(streams, on_event)
