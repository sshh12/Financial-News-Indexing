from finnews.articles import ARTICLE_SOURCES
from finnews.articles.utils import extract_symbols
from finnews.utils import hash_sha1, config
from finnews.stream.abs import StreamPoll
import asyncio
import aiohttp


CFG = config["watch"].get("news", {})


class StreamNews(StreamPoll):
    def __init__(self):
        self.scrapers = [ARTICLE_SOURCES[name]() for name in CFG["sources"]]
        self.cache = set()
        self.delay = CFG["delay"]

    async def get_polls(self):
        polls = []
        for scrap in self.scrapers:

            def make_scrap(news_cls):
                async def scrap_news():
                    try:
                        return await news_cls.read_latest_headlines()
                    except asyncio.TimeoutError:
                        return "", []
                    except aiohttp.ClientError:
                        return "", []

                return scrap_news

            polls.append((scrap, make_scrap(scrap), self.delay))
        return polls

    async def _resolve_and_add_evt(self, scraper, evt):
        url = evt.get("url", "")
        try:
            text = await scraper.resolve_url_to_content(url)
        except Exception as e:
            text = None
            self.on_event(dict(type="error", name="polling", desc=repr(e), source=str(scraper)))
        if text is None:
            self.on_event(evt)
        else:
            evt["text"] = text
            evt["symbols"] = list(set(evt["symbols"]) | extract_symbols(text, strict=True))
            self.on_event(evt)

    async def on_poll_data(self, source, headlines, obj=None, emit_empty=False, emit_events=True, **kwargs):
        if len(headlines) == 0 and emit_empty:
            self.on_event(dict(type="error", name="empty", desc=source, source=str(self)))
        evts_to_emit = []
        for item in headlines:
            if len(item) == 2:
                url, headline = item
                text = ""
            elif len(item) == 3:
                url, headline, text = item
            key = hash_sha1(url + headline)
            if key not in self.cache and emit_events:
                data = dict(
                    source=source,
                    type="article",
                    title=headline,
                    url=url,
                    text=text,
                    symbols=list(extract_symbols(headline)),
                )
                evts_to_emit.append(data)
            self.cache.add(key)
        if len(evts_to_emit) > 0:
            await asyncio.gather(*[self._resolve_and_add_evt(obj, evt) for evt in evts_to_emit])
