from config import config
from stats.guru import Guru
from . import StreamPoll
import asyncio
import aiohttp


CFG = config['watch']['guru']


class StreamGuru(StreamPoll):

    def __init__(self):
        self.scraper = Guru()
        self.hist = {}
        self.stocks = CFG['stocks']
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
        prev = self.hist.get(sym)
        self.hist[sym] = fin_data.copy()
        if prev is not None:
            diff_data = {}
            for key, og_val in prev.items():
                new_val = fin_data.get(key, og_val)
                if type(og_val) != type(new_val) or og_val == new_val:
                    continue
                if type(new_val) in [int, float]:
                    diff = new_val - og_val
                    if og_val != 0:
                        diffp = diff / og_val
                    else:
                        diffp = 0
                    diff_data[key + '_diff'] = diff
                    diff_data[key + '_diffpercent'] = diffp
                else:
                    diff_data[key + '_new'] = new_val
                    diff_data[key + '_prev'] = og_val
            if len(diff_data) > 0:
                diff_data.update(dict(source=source, type='financials', name='guru-diff', symbols=[sym]))
                self.on_event(diff_data)
        fin_data.update(dict(source=source, type='financials', name='guru-spot', symbols=[sym]))
        self.on_event(fin_data)