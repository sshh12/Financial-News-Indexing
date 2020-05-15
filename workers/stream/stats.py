from config import config
from articles import hash_sha1
from stats.finviz import FinViz
from . import StreamPoll
import asyncio
import aiohttp


CFG = config['watch']['stats']
SOURCES = {
    'finviz': FinViz
}


class StreamStats(StreamPoll):

    def __init__(self):
        self.scrapers = [SOURCES[name]() for name in CFG['sources']]
        self.cache = set()
        self.delay = CFG['delay']

    async def _poll(self, emit_empty=True, emit_events=True):
        async with aiohttp.ClientSession() as session:
            for scrap in self.scrapers:
                scrap._session = session
            fetch_tasks = [scrap.read_stats() for scrap in self.scrapers]
            for name, stats in await asyncio.gather(*fetch_tasks):
                if len(stats) == 0 and emit_empty:
                    self.on_event(dict(type='error', name='empty', desc=name, source=str(self)))
                for stat in stats:
                    key = hash_sha1(repr(stat))
                    if key not in self.cache and emit_events:
                        self.on_event(stat)
                    self.cache.add(key)