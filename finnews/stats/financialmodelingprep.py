from . import TradeRating, SymbolList, GroupStats, MetaDataSource

import asyncio
import json


class FinancialModelingPrep(MetaDataSource):
    def __init__(self, symbols=[]):
        self.url = "https://financialmodelingprep.com"
        self.symbols = symbols

    async def _call_api(self, path):
        data = await self._get("/api/v3/{}".format(path))
        return json.loads(data)

    async def read_rating(self, symbol):
        resp = await self._call_api("company/rating/{}".format(symbol))
        if "rating" not in resp:
            return None
        scores = {"overall": resp["rating"]}
        for name in resp["ratingDetails"]:
            scores[name] = resp["ratingDetails"][name]
        return TradeRating(symbol, "fmp", scores)

    async def read_ratings(self):
        ratings = []
        fetch_tasks = [self.read_rating(symbol.upper()) for symbol in self.symbols]
        for symbol_rating in await asyncio.gather(*fetch_tasks):
            if symbol_rating is not None:
                ratings.append(symbol_rating)
        return ratings

    async def read_list(self, path):
        resp = await self._call_api(path)
        if "error" in resp:
            return None
        name = list(resp.keys())[0]
        items = []
        for item_json in resp[name]:
            items.append(
                dict(
                    symbol=item_json["ticker"],
                    delta_price=float(item_json["changes"]),
                    delta_percent=float(
                        item_json["changesPercentage"].replace("%", "").replace(")", "").replace("(", "")
                    ),
                )
            )
        list_ = SymbolList(name, "fmp", items)
        return list_

    async def read_lists(self):
        lists = []
        fetch_tasks = [self.read_list(path) for path in ["stock/actives", "stock/gainers", "stock/losers"]]
        for list_data in await asyncio.gather(*fetch_tasks):
            if list_data is not None:
                lists.append(list_data)
        return lists

    async def read_group_stats(self):
        sectors_resp = await self._call_api("stock/sectors-performance")
        items = {}
        for item_json in sectors_resp["sectorPerformance"]:
            items.update(
                {
                    item_json["sector"]: {
                        "delta_percent": float(
                            item_json["changesPercentage"].replace("%", "").replace(")", "").replace("(", "")
                        )
                    }
                }
            )
        groups = [GroupStats("sectors", "fmp", items)]
        return groups
