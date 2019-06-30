import pendulum
import hashlib


USE_TZ = 'UTC'
HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
}


class PriceTick:

    def __init__(self, symbol, date, open_, high, low, close, volume):
        self.symbol = symbol
        self.date = date
        self.open = float(open_)
        self.high = float(high)
        self.low = float(low)
        self.close = float(close)
        self.volume = float(volume)
        self.found = pendulum.now().in_tz(USE_TZ)
        self._id = hash_sha1(self.symbol + str(self.date))

    def __repr__(self):
        return '<Tick [{}] ({} @ {})>'.format(self.symbol, self.close, self.date)
        
    def as_dict(self):
        return {
        }


class TickDataSource:

    async def _get(self, url_part):
        try:
            async with self._session.get(self.url + url_part, headers=HEADERS) as response:
                return await response.text()
        except (ConnectionRefusedError, UnicodeDecodeError):
            return ''



def hash_sha1(text):
    return hashlib.sha1(bytes(text, 'utf-8')).hexdigest()