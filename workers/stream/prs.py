from articles.releases import SCRAPERS
from config import config
from . import Stream
import asyncio
import aiohttp


CFG = config['watch']['prs']


class StreamPRs(Stream):

    def __init__(self):
        self.scrapers = [Scraper() for Scraper in SCRAPERS[:10]]
        self.cache = set()

    def start(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._run())

    async def _run(self):
        i = 0
        while True:
            try:
                await self._poll(print_empty=(i == 0), emit_events=(i > 0))
            except Exception as e:
                print('Poll error', e)
            await asyncio.sleep(CFG['delay'])
            i += 1

    async def _poll(self, print_empty=True, emit_events=True):
        async with aiohttp.ClientSession() as session:
            for scrap in self.scrapers:
                scrap._session = session
            fetch_tasks = [scrap.read_prs() for scrap in self.scrapers]
            for symbol, name, prs in await asyncio.gather(*fetch_tasks):
                if len(prs) == 0 and print_empty:
                    print('WARN: nothing found for', name)
                for pr in prs:
                    key = (symbol, pr.headline)
                    if key not in self.cache and emit_events:
                        data = dict(source=name, type='pr', title=pr.headline, 
                            url=pr.url, published=pr.date, symbols=[symbol])
                        self.on_event(data)
                    self.cache.add(key)