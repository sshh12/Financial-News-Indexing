from articles.seekingalpha import SeekingAlpha
from articles.marketwatch import MarketWatch
from articles import extract_symbols
from config import config
from . import StreamPoll
import asyncio
import aiohttp


CFG = config['watch']['news']


class StreamNews(StreamPoll):

    def __init__(self):
        self.scrapers = [MarketWatch(), SeekingAlpha()]
        self.cache = set()
        self.delay = CFG['delay']

    async def _poll(self, print_empty=True, emit_events=True):
        async with aiohttp.ClientSession() as session:
            for scrap in self.scrapers:
                scrap._session = session
            fetch_tasks = [scrap.read_latest_headlines() for scrap in self.scrapers]
            for source, headlines in await asyncio.gather(*fetch_tasks):
                if len(headlines) == 0 and print_empty:
                    print('WARN: no news found for', source)
                for url, headline in headlines:
                    key = (url, headline)
                    if key not in self.cache and emit_events:
                        data = dict(source=source, type='article', title=headline, 
                            url=url, symbols=list(extract_symbols(headline)))
                        self.on_event(data)
                    self.cache.add(key)