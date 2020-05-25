from config import config
from . import StreamPoll
from stats.sec import SEC
import asyncio
import aiohttp


CFG = config['watch']['sec']


class StreamSEC(StreamPoll):

    def __init__(self):
        self.scraper = SEC()
        self.cache = set()
        self.delay = CFG['delay']

    async def get_polls(self):
        return [(self.scraper, self.scraper.read_latest_filings, self.delay)]

    async def on_poll_data(self, source, filings, emit_empty=False, emit_events=True, **kwargs):
        emit_events = True
        if len(filings) == 0 and emit_empty:
            self.on_event(dict(type='error', name='empty', desc='', source=str(self)))
        for title, url in filings:
            if url not in self.cache and emit_events:
                data = await self.scraper.resolve_filing(url)
                if data is None:
                    continue
                data.update(dict(source='sec', type='filing', title=title))
                self.on_event(data)
            self.cache.add(url)