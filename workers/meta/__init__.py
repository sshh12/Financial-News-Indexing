import pendulum
import hashlib


USE_TZ = 'UTC'
HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
}


class TradeRating:

    def __init__(self, symbol, source, scores):
        self.symbol = symbol
        self.source = source
        self.scores = scores
        self.found = pendulum.now().in_tz(USE_TZ)
        self._id = hash_sha1(self.symbol + str(self.found))
        
    def as_dict(self):
        data = {
            'symbol': self.symbol,
            'source': self.source,
            'found': self.found
        }
        data.update(self.scores)
        return data


class MetaDataSource:

    async def _get(self, url_part):
        try:
            async with self._session.get(self.url + url_part, headers=HEADERS) as response:
                return await response.text()
        except (ConnectionRefusedError, UnicodeDecodeError):
            return ''



def hash_sha1(text):
    return hashlib.sha1(bytes(text, 'utf-8')).hexdigest()