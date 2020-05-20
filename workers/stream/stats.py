from config import config
from articles import hash_sha1
from stats.finviz import FinViz
from stats.zacks import Zacks
from stats.earningscast import EarningsCast
from . import StreamPoll
import asyncio
import aiohttp


CFG = config['watch']['stats']
SOURCES = {
    'finviz': FinViz,
    'zacks': Zacks,
    'earningscast': EarningsCast
}


class StreamStats(StreamPoll):

    def __init__(self):
        self.scrapers = [SOURCES[name]() for name in CFG['sources']]
        self.cache = set()
        self.delay = CFG['delay']

    async def get_polls(self):
        polls = []
        for scrap in self.scrapers:
            polls.append((scrap, scrap.read_stats, self.delay))
        return polls

    def on_poll_data(self, name, stats, emit_empty=False, emit_events=True):
        if len(stats) == 0 and emit_empty:
            self.on_event(dict(type='error', name='empty', desc=name, source=str(self)))
        for stat in stats:
            key = hash_sha1(repr(stat))
            if key not in self.cache and emit_events:
                self.on_event(stat)
            self.cache.add(key)