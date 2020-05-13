from articles.releases import SCRAPERS
from config import config
from . import StreamPoll
import asyncio
import aiohttp


CFG = config['watch']['prs']


class StreamPRs(StreamPoll):

    def __init__(self):
        self.scrapers = [Scraper() for Scraper in SCRAPERS[:10]]
        self.cache = set()
        self.delay = CFG['delay']

    async def _poll(self, emit_empty=True, emit_events=True):
        async with aiohttp.ClientSession() as session:
            for scrap in self.scrapers:
                scrap._session = session
            fetch_tasks = [scrap.read_prs() for scrap in self.scrapers]
            for symbol, name, prs in await asyncio.gather(*fetch_tasks):
                if len(prs) == 0 and emit_empty:
                    self.on_event(dict(type='error', name='empty', desc=name, source=str(self)))
                for pr in prs:
                    key = (symbol, pr.headline)
                    if key not in self.cache and emit_events:
                        data = dict(source=name, type='pr', title=pr.headline, 
                            url=pr.url, published=pr.date, symbols=[symbol])
                        self.on_event(data)
                    self.cache.add(key)