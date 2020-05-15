from . import MetaDataSource
from articles import clean_html_text, extract_symbols
import re


TABLE_REGEX = r'>([A-Z\.]+)<\/a>[\s\S]+?link">([\w \',\.]+?)<[\s\S]+?">([\w%,\.&/]+?)<[\s\S]+?">(\w+? \d+?)<[\s\S]+?center">([\w ]+?)<[\s\S]+?\[\d+\]">([\d\.]+?)<[\s\S]+?right">([\d,]+?)<[\s\S]+?right">([\d,]+?)<[\s\S]+?right">([\d,]+?)<'


class FinViz(MetaDataSource):

    def __init__(self):
        self.url = 'https://finviz.com'

    async def read_latest_headlines(self):
        resp = await self._get('/news.ashx')
        headlines = []
        for match in re.finditer(r']"><a href="([^"]+?)" target="_blank" class="nn-tab-link">([^<]+?)<', resp):
            headline = clean_html_text(match.group(2))
            url = match.group(1)
            headlines.append((url, headline))
        return headlines

    async def read_insider_trades(self):
        resp = await self._get('/insidertrading.ashx')
        trades = []
        for match in re.finditer(TABLE_REGEX, resp):
            row = [match.group(i) for i in range(1, 10)]
            try:
                row[4] = row[4].upper()
                row[5] = float(row[5].replace(',', ''))
                row[6] = float(row[6].replace(',', ''))
                row[7] = float(row[7].replace(',', ''))
                row[8] = float(row[8].replace(',', ''))
            except:
                pass
            trades.append(row)
        return trades

    async def read_stats(self):
        stats = []
        headlines = await self.read_latest_headlines()
        for url, headline in headlines:
            stats.append(dict(source='finviz', type='article', 
                title=headline, url=url, symbols=list(extract_symbols(headline))
            ))
        trades = await self.read_insider_trades()
        for trade in trades:
            stats.append(dict(source='finviz', type='insidetrade',
                fullname=trade[1], position=trade[2], date=trade[3], action=trade[4],
                cost=trade[5], shares=trade[6], value=trade[7], shares_total=trade[8],
                symbols=[trade[0]]
            ))
        return 'finviz', stats