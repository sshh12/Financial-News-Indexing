from collections import defaultdict
from pymeritrade import TDAClient
from threading import Thread
from config import config
from . import Stream
import pendulum
import time
import os


CREDS = config['creds']['tda']
CFG = config['watch']['tda']


class StreamTDA(Stream):

    def __init__(self):
        self.tda = TDAClient(CREDS['consumer_key'])
        self.tda.load_login(os.path.join('data', 'tda-login'))
        self.stream = self.tda.create_stream(debug=False)
        self.stocks = CFG.get('stocks', config['symbols_list_all'])
        self.delay_prices = CFG.get('delay_prices', 60 * 60)
        self.warmup_period = CFG.get('warmup', 30)
        
        self.warmup = True
        self.opt_error_rate = defaultdict(lambda: 0)

    def start(self):
        self.quote_thread = Thread(target=self._start_quotes)
        self.quote_thread.start()
        self.stream.start()
        self.stream.subscribe('news', symbols=self.stocks, fields=[0, 5, 9, 10])
        time_start = time.time()
        for id_, item in self.stream.live_data():
            if self.warmup and time.time() - time_start < self.warmup_period:
                # flush old news
                continue
            else:
                self.warmup = False
            for data_type, stream_data in item.items():
                evt = self._news_to_evt(stream_data)
                if evt is not None:
                    self.on_event(evt)

    def _start_quotes(self):
        while True:
            for stock in self.stocks:
                ts = int(pendulum.now().timestamp() * 100)
                price_fn = os.path.join('data', 'watch', 'ticks', 'P_{}_{}.csv'.format(stock, ts))
                options_fn = os.path.join('data', 'watch', 'ticks', 'O_{}_{}.csv'.format(stock, ts))
                try:
                    self.tda.history(span='day', freq='minute', latest=True)[stock].to_csv(price_fn)
                except Exception as e:
                    err = str(e)
                    if 'transactions per seconds restriction' in err:
                        time.sleep(2)
                    else:
                        self.on_event(dict(symbols=[stock], type='error', name='tda-price', desc=err, source=str(self)))
                try:
                    if self.opt_error_rate[stock] < 0.5:
                        self.tda.options(quotes=True)[stock].to_csv(options_fn)
                except Exception as e:
                    err = str(e)
                    self.opt_error_rate[stock] = self.opt_error_rate[stock] * 0.75 + 0.25
                    if 'transactions per seconds restriction' in err:
                        time.sleep(2)
                    else:
                        self.on_event(dict(symbols=[stock], type='error', name='tda-options', desc=err, source=str(self)))
            time.sleep(self.delay_prices)

    def _news_to_evt(self, news):
        evt = dict(title=news['5'], type='article', source=news['10'], hot=news['9'], symbols=[news['key']])
        if evt['title'] == 'N/A':
            return None
        return evt