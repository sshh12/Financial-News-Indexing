from finnews.articles.releases import SCRAPERS
from finnews.config import config
from finnews.stream.abs import StreamPoll
import asyncio
import aiohttp


CFG = config["watch"].get("prs", {})


class StreamPRs(StreamPoll):
    def __init__(self):
        self.scrapers = [Scraper() for Scraper in SCRAPERS]
        self.cache = set()
        self.delay = CFG["delay"]

    async def get_polls(self):
        polls = []
        for scrap in self.scrapers:

            def make_scrap(pr_cls):
                async def scrap_prs():
                    try:
                        return await pr_cls.read_prs()
                    except asyncio.TimeoutError:
                        return "", "", []
                    except aiohttp.ClientError:
                        return "", "", []

                return scrap_prs

            polls.append((scrap, make_scrap(scrap), self.delay))
        return polls

    async def on_poll_data(self, symbol, name, prs, emit_empty=False, emit_events=True, **kwargs):
        if len(prs) == 0 and emit_empty:
            self.on_event(dict(type="error", name="empty", desc=name, source=str(self)))
        for pr in prs:
            pr_source, pr_title, pr_date, pr_content, pr_url = pr
            key = (symbol, pr_title)
            if key not in self.cache and emit_events:
                data = dict(
                    source=name, type="pr", title=pr_title, url=pr_url, published=str(pr_date), symbols=[symbol]
                )
                self.on_event(data)
            self.cache.add(key)
