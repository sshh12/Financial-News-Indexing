from config import config
from articles import hash_sha1
from stats.index import STAT_SOURCES
from . import StreamPoll
import asyncio
import aiohttp


CFG = config["watch"]["stats"]


class StreamStats(StreamPoll):
    def __init__(self):
        self.scrapers = [STAT_SOURCES[name]() for name in CFG["sources"]]
        self.cache = set()
        self.delay = CFG["delay"]

    async def get_polls(self):
        polls = []
        for scrap in self.scrapers:
            polls.append((scrap, scrap.read_stats, self.delay))
        return polls

    async def on_poll_data(self, name, stats, emit_empty=False, emit_events=True, **kwargs):
        if len(stats) == 0 and emit_empty:
            self.on_event(dict(type="error", name="empty", desc=name, source=str(self)))
        for stat in stats:
            key = hash_sha1(repr(stat))
            if key not in self.cache and emit_events:
                self.on_event(stat)
            self.cache.add(key)
