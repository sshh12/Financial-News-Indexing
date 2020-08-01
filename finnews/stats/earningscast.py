from finnews.stats.abs import MetaDataSource
import pendulum
import json
import re


class EarningsCast(MetaDataSource):
    def __init__(self):
        self.url = "https://earningscast.com"

    async def read_earnings(self):
        resp = await self._get("/")
        earnings = []
        for match in re.finditer(
            r'Act ([\-\.\d]+) <br \/>\s*?Est ([\-\.\d]+)\s*?<\/div>\s*?<[\w= "]+?><a href="\/([\w\.]+?)\/', resp
        ):
            sym = match.group(3)
            est = match.group(1)
            act = match.group(2)
            earnings.append((sym, est, act))
        return earnings

    async def read_stats(self):
        stats = []
        earnings = await self.read_earnings()
        for sym, est, act in earnings:
            stats.append(dict(source="earningscast", type="earnings", symbols=[sym], expected=est, actual=act))
        return "earningscast", stats

