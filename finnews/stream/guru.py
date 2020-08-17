from finnews.utils import config, ensure_dirs
from finnews.stats.guru import Guru
from finnews.stream.abs import StreamPoll
import pendulum
import asyncio
import aiohttp
import random
import json
import os


CFG = config["watch"].get("guru")


class StreamGuru(StreamPoll):
    def __init__(self):
        self.scraper = Guru()
        self.stocks = CFG.get("stocks", config["symbols_list_all"])
        self.delay = CFG["delay"]
        self.save_dir = os.path.join(config["data_dir"], "watch", "fin")
        ensure_dirs([self.save_dir])

    async def get_polls(self):
        polls = []
        for stock in self.stocks:

            def make_scrap(sym=None):
                async def scrap_stock():
                    await asyncio.sleep(random.randint(0, 60 * 60))
                    try:
                        return await self.scraper.read_financials(sym)
                    except Exception as e:
                        self.on_event(
                            dict(
                                symbols=[sym],
                                type="error",
                                name="guru-data",
                                desc=str(e),
                                source=str(self),
                                error=repr(e),
                            )
                        )
                        return None, None, None

                return scrap_stock

            polls.append((self.scraper, make_scrap(sym=stock), self.delay))
        return polls

    async def on_poll_data(self, source, sym, fin_data, emit_events=True, **kwargs):
        if sym is None or fin_data is None:
            return
        spot_evt = dict(
            source=source,
            type="financials",
            name="guru-spot",
            ts=pendulum.now().timestamp(),
            symbols=[sym],
            _data_evt=True,
            _data=fin_data,
            _data_fn=os.path.join(self.save_dir, "G_" + sym),
        )
        self.on_event(spot_evt)

