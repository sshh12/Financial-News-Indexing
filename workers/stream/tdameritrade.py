from pymeritrade import TDAClient
from config import config
from . import Stream
import time
import os


CREDS = config['creds']['tda']
CFG = config['watch']['tda']


class StreamTDA(Stream):

    def __init__(self):
        self.tda = TDAClient(CREDS['consumer_key'])
        self.tda.load_login(os.path.join('data', 'tda-login'))
        self.stream = self.tda.create_stream(debug=False)

    def start(self):
        self.stream.start()
        self.stream.subscribe('news', symbols=CFG['news'], fields=[0, 5, 9, 10])
        time_start = time.time()
        for id_, item in self.stream.live_data():
            if time.time() - time_start < 30:
                # flush old news
                continue
            for key, stream_data in item.items():
                evt = self._news_to_evt(stream_data)
                if evt is not None:
                    self.on_event(evt)

    def _news_to_evt(self, news):
        evt = dict(title=news['5'], type='article', source=news['10'], hot=news['9'], symbols=[news['key']])
        if evt['title'] == 'N/A':
            return None
        return evt