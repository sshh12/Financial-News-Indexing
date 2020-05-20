from articles.seekingalpha import SeekingAlpha
from articles.marketwatch import MarketWatch
from articles.reuters import Reuters
from articles.prnewswire import PRNewsWire
from articles.rttnews import RTTNews
from articles.moodys import Moodys
from articles.businesswire import BusinessWire
from articles.federalreserve import FederalReserve
from articles.globenewswire import GlobeNewsWire
from articles.accesswire import AccessWire
from articles.stocktwits import StockTwits
from articles.usbls import USBLS
from articles.stat import STAT
from articles.fitch import Fitch
from articles.thestreet import TheStreet
from articles.cnn import CNN
from articles.barrons import Barrons
from articles import extract_symbols, hash_sha1
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
    'globenewswire': GlobeNewsWire,
    'accesswire': AccessWire,
    'stocktwits': StockTwits,
    'stat': STAT,
    'fitch': Fitch,
    'thestreet': TheStreet,
    'barrons': Barrons,
    'cnn': CNN
}


class StreamNews(StreamPoll):

    def __init__(self):
        self.scrapers = [SOURCES[name]() for name in CFG['sources']]
        self.cache = set()
        self.delay = CFG['delay']

    async def get_polls(self):
        polls = []
        for scrap in self.scrapers:
            polls.append((scrap, scrap.read_latest_headlines, self.delay))
        return polls

    async def _resolve_and_add_evt(self, scraper, evt):
        url = evt.get('url', '')
        try:
            text = await scraper.resolve_url_to_content(url)
        except Exception as e:
            text = None
            self.on_event(dict(type='error', name='polling', desc=repr(e), source=str(scraper)))
        if text is None:
            self.on_event(evt)
        else:
            evt['text'] = text
            evt['symbols'] = list(set(evt['symbols']) | extract_symbols(text, strict=True))
            self.on_event(evt)

    async def on_poll_data(self, source, headlines, obj=None, emit_empty=False, emit_events=True, **kwargs):
        if len(headlines) == 0 and emit_empty:
            self.on_event(dict(type='error', name='empty', desc=source, source=str(self)))
        evts_to_emit = []
        for item in headlines:
            if len(item) == 2:
                url, headline = item
                text = ''
            elif len(item) == 3:
                url, headline, text = item
            key = hash_sha1(url + headline)
            if key not in self.cache and emit_events:
                data = dict(source=source, type='article', title=headline, 
                    url=url, text=text, symbols=list(extract_symbols(headline)))
                evts_to_emit.append(data)
            self.cache.add(key)
        if len(evts_to_emit) > 0:
            await asyncio.gather(*[self._resolve_and_add_evt(obj, evt) for evt in evts_to_emit])