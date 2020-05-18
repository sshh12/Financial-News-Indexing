from . import MetaDataSource
import pendulum
import json
import re


class Zacks(MetaDataSource):

    def __init__(self):
        self.url = 'https://www.zacks.com'

    async def read_earnings(self):
        resp = await self._get('/research/earnings/z2_earnings_tab_data.php?type=1')
        resp_json = json.loads(resp)
        earnings = []
        for item in resp_json['data']:
            sym = re.search(r'quote\/([A-Z\.]+)"', item[0].replace('*', '')).group(1)
            report_time = item[2]
            est = item[3]
            actual = item[4]
            suprise = item[5]
            earnings.append((sym, report_time, est, actual, suprise))
        return earnings

    async def read_stats(self):
        stats = []
        earnings = await self.read_earnings()
        for sym, report, est, act, sup in earnings:
            stats.append(dict(source='zacks', type='earnings',
                symbols=[sym], event_time=report, expected=est, actual=act
            ))
        return 'zacks', stats