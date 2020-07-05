from finnews.articles.releases import SCRAPERS
from finnews.config import config
from finnews.stream.abs import StreamPoll
import asyncio
import aiohttp


CFG = config["watch"]["prs"]


class StreamPRs(StreamPoll):
    def __init__(self):
        self.scrapers = [Scraper() for Scraper in SCRAPERS]
        self.cache = set()
        self.delay = CFG["delay"]

    async def get_polls(self):
        polls = []
        for scrap in self.scrapers:
            polls.append((scrap, scrap.read_prs, self.delay))
        return polls

    async def on_poll_data(self, symbol, name, prs, emit_empty=False, emit_events=True, **kwargs):
        if len(prs) == 0 and emit_empty:
            self.on_event(dict(type="error", name="empty", desc=name, source=str(self)))
        for pr in prs:
            key = (symbol, pr.headline)
            if key not in self.cache and emit_events:
                data = dict(
                    source=name, type="pr", title=pr.headline, url=pr.url, published=str(pr.date), symbols=[symbol]
                )
                self.on_event(data)
            self.cache.add(key)
