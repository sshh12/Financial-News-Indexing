from finnews.stats.abs import MetaDataSource
from finnews.articles.utils import clean_html_text, extract_symbols
import pendulum
import re


INSIDER_REGEX = r'>([A-Z\.]+)<\/a>[\s\S]+?link">([\w \',\.]+?)<[\s\S]+?">([\w%,\.&/]+?)<[\s\S]+?">(\w+? \d+?)<[\s\S]+?center">([\w ]+?)<[\s\S]+?\[\d+\]">([\d\.]+?)<[\s\S]+?right">([\d,]+?)<[\s\S]+?right">([\d,]+?)<[\s\S]+?right">([\d,]+?)<'
HEADLINES_REGEX = r']"><a href="([^"]+?)" target="_blank" class="nn-tab-link">([^<]+?)<'
SIGNALS_REGEX = r'tab-link">([A-Z\.]+?)<[\S\s]+?tab-link-nw">([\w ]+?)<'
CALENDAR_REGEX = r'<td align="right">([\d:APM ]+?)<[\s\S]+?"left">([\w\d,\-\. ]+?)<[\s\S]+?impact_(\d+).gif[\s\S]+?ft">([^<]+?)<[\/td><\n align="rh]+>([^<]+?)<[\/td><\n align="rh]+>([^<]+?)<[\/td><\n align="rh]+>([^<]+?)<'
SIGNALS = set(
    [
        "Top Gainers",
        "New High",
        "Over Bought",
        "Unusual Volume",
        "Upgrades",
        "Earnings Before",
        "Insider Buying",
        "Top Losers",
        "New Low",
        "Most Volatile",
        "Most Active",
        "Downgrades",
        "Earnings After",
        "Insider Selling",
    ]
)
IMPACTS = {"1": "LOW", "2": "MEDIUM", "3": "HIGH"}


class FinViz(MetaDataSource):
    def __init__(self):
        self.url = "https://finviz.com"

    async def read_latest_headlines(self):
        resp = await self._get("/news.ashx")
        headlines = []
        for match in re.finditer(HEADLINES_REGEX, resp):
            headline = clean_html_text(match.group(2))
            url = match.group(1)
            headlines.append((url, headline))
        return headlines

    async def read_insider_trades(self):
        resp = await self._get("/insidertrading.ashx")
        trades = []
        for match in re.finditer(INSIDER_REGEX, resp):
            row = [match.group(i) for i in range(1, 10)]
            try:
                row[4] = row[4].upper()
                row[5] = float(row[5].replace(",", ""))
                row[6] = float(row[6].replace(",", ""))
                row[7] = float(row[7].replace(",", ""))
                row[8] = float(row[8].replace(",", ""))
            except:
                pass
            trades.append(row)
        return trades

    async def read_signals(self):
        resp = await self._get("")
        sigs = []
        for match in re.finditer(SIGNALS_REGEX, resp):
            sym = match.group(1)
            sig = match.group(2)
            if sig not in SIGNALS:
                continue
            sigs.append((sym, sig))
        return sigs

    async def read_calendar(self):
        resp = await self._get("/calendar.ashx")
        resp = re.sub(r'<span style="color:#[\w\d]+;">', "", resp)
        resp = re.sub(r"<\/span>", "", resp)
        events = []
        for match in re.finditer(CALENDAR_REGEX, resp):
            event = [match.group(i) for i in range(1, 8)]
            if event[4].strip() == "-":
                continue
            events.append(event)
        return events

    async def read_stats(self):
        date = pendulum.today().isoformat()[:10]
        stats = []
        headlines = await self.read_latest_headlines()
        for url, headline in headlines:
            stats.append(
                dict(source="finviz", type="article", title=headline, url=url, symbols=list(extract_symbols(headline)))
            )
        trades = await self.read_insider_trades()
        for trade in trades:
            stats.append(
                dict(
                    source="finviz",
                    type="insidetrade",
                    fullname=trade[1],
                    position=trade[2],
                    event_date=trade[3],
                    name=trade[4],
                    cost=trade[5],
                    shares=trade[6],
                    value=trade[7],
                    shares_total=trade[8],
                    symbols=[trade[0]],
                )
            )
        sigs = await self.read_signals()
        for sym, sig in sigs:
            stats.append(dict(source="finviz", type="signal", name=sig, symbols=[sym], event_time=date))
        events = await self.read_calendar()
        for event in events:
            stats.append(
                dict(
                    source="finviz",
                    type="calendar",
                    event_time=event[0],
                    name=event[1],
                    impact=IMPACTS.get(event[2]),
                    event_for=event[3],
                    actual=event[4],
                    expected=event[5],
                    prev=event[6],
                )
            )
        return "finviz", stats

