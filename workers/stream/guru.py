from config import config
from stats.guru import Guru
from . import StreamPoll
import asyncio
import aiohttp


CFG = config['watch']['guru']


class StreamGuru(StreamPoll):

    def __init__(self):
        self.scraper = Guru()
        self.stocks = CFG.get('stocks', config['symbols_list_all'])
        self.delay = CFG['delay']

    async def get_polls(self):
        polls = []
        for stock in self.stocks:
            def make_scrap(sym=None):
                async def scrap_stock():
                    return await self.scraper.read_financials(sym)
                return scrap_stock
            polls.append((self.scraper, make_scrap(sym=stock), self.delay))
        return polls

    async def on_poll_data(self, source, sym, fin_data, emit_events=True, **kwargs):
        fin_data.update(dict(source=source, type='financials', name='guru-spot', symbols=[sym]))
        self.on_event(fin_data)