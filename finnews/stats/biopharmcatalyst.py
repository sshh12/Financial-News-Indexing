from . import MetaDataSource
import pendulum
import json
import re


class BioPharmCatalyst(MetaDataSource):
    def __init__(self):
        self.url = "https://www.biopharmcatalyst.com"

    async def read_fda_calendar(self):
        resp = await self._get("/calendars/fda-calendar")
        resp = re.search(r'<screener :pro="0" :tabledata="([^"]+?)"><\/screener>', resp).group(1)
        resp = resp.replace("&quot;", '"')
        resp_data = json.loads(resp)
        events = []
        for item in resp_data:
            try:
                sym = item["companies"]["ticker"]
                url = item["press_link"]
                ind = item["indication"]
                name = item["name"]
                note = item["note"]
                stage = item["stage"]["id"]
                events.append((sym, url, ind, name, note, stage))
            except:
                pass
        return events

    async def read_stats(self):
        stats = []
        events = await self.read_fda_calendar()
        for sym, url, ind, name, note, stage in events:
            stats.append(
                dict(
                    source="biopharmcatalyst",
                    type="fda-calendar",
                    url=url,
                    name=ind,
                    drug=name,
                    stage=stage,
                    text=note,
                    symbols=[sym],
                )
            )
        return "biopharmcatalyst", stats

