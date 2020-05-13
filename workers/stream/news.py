from articles.seekingalpha import SeekingAlpha
from articles.marketwatch import MarketWatch
from articles.reuters import Reuters
from articles.prnewswire import PRNewsWire
from articles.rttnews import RTTNews
from articles.moodys import Moodys
from articles.businesswire import BusinessWire
from articles.federalreserve import FederalReserve
from articles.globenewswire import GlobeNewsWire
from articles.usbls import USBLS
from articles import extract_symbols
from config import config
from . import StreamPoll
import asyncio
import aiohttp


CFG = config['watch']['news']
SOURCES = {
    'prnewswire': PRNewsWire,
    'reuters': Reuters,
    'marketwatch': MarketWatch,
    'seekingalpha': SeekingAlpha,
    'rtt': RTTNews,
    'moodys': Moodys,
    'businesswire': BusinessWire,
    'federalreserve': FederalReserve,
    'usbls': USBLS,
    'globenewswire': GlobeNewsWire
}


class StreamNews(StreamPoll):

    def __init__(self):
        self.scrapers = [SOURCES[name]() for name in CFG['sources']]
        self.cache = set()
        self.delay = CFG['delay']

    async def _poll(self, emit_empty=True, emit_events=True):
        async with aiohttp.ClientSession() as session:
            for scrap in self.scrapers:
                scrap._session = session
            fetch_tasks = [scrap.read_latest_headlines() for scrap in self.scrapers]
            for source, headlines in await asyncio.gather(*fetch_tasks):
                if len(headlines) == 0 and emit_empty:
                    self.on_event(dict(type='error', name='empty', desc=source, source=str(self)))
                for url, headline in headlines:
                    key = (url, headline)
                    if key not in self.cache and emit_events:
                        data = dict(source=source, type='article', title=headline, 
                            url=url, symbols=list(extract_symbols(headline)))
                        self.on_event(data)
                    self.cache.add(key)