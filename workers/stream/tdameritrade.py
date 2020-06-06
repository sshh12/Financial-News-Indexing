from collections import defaultdict
from pymeritrade import TDAClient
from threading import Thread
from config import config
from . import Stream
import pendulum
import random
import time
import os


CREDS = config['creds']['tda']
CFG = config['watch']['tda']


class StreamTDA(Stream):

    def __init__(self):
        self.tda = TDAClient(CREDS['consumer_key'])
        try:
            self.tda.load_login(os.path.join('data', 'tda-login'))
        except FileNotFoundError:
            self.tda.login()
            self.tda.save_login(os.path.join('data', 'tda-login'))
        self.stream = self.tda.create_stream(debug=False)
        self.symbols = CFG.get('stocks', config['symbols_list_all'])
        self.delay_prices = CFG.get('delay_prices', 60 * 60)
        self.warmup_period = CFG.get('warmup', 30)
        
        self.warmup = True
        self.quotes_cnt = 0
        self.quote_err = defaultdict(lambda: 0)

    def start(self):
        self.quote_thread = Thread(target=self._start_quotes)
        self.quote_thread.start()
        self.stream.start()
        self.stream.subscribe('news', symbols=self.symbols, fields=[0, 5, 9, 10])
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
        symbols = list(self.symbols)\
             + ['FUTUREES', 'FUTUREGC', 'FUTUREBTC', 'FUTURECL']\
             + ['EURCURRVSUSD', 'USDCURRVSJPY']
        while True:
            # shuffle to avoid consistent rate limits on symbols
            random.shuffle(symbols)
            for symbol in symbols:
                if self.quotes_cnt > 10 and self.quote_err[symbol] / self.quotes_cnt > 0.5:
                    continue
                ts = int(pendulum.now().timestamp() * 1000)
                price_fn = os.path.join('data', 'watch', 'ticks', 'P_{}_{}.csv'.format(symbol, ts))
                options_fn = os.path.join('data', 'watch', 'ticks', 'O_{}_{}.csv'.format(symbol, ts))
                tda_sym = symbol.replace('FUTURE', '/').replace('CURRVS', '/')
                try:
                    self.tda.history(span='day', freq='minute', latest=True)[tda_sym].to_csv(price_fn)
                    try:
                        # tbh options data is just extra
                        time.sleep(1)
                        self.tda.options(quotes=True)[tda_sym].to_csv(options_fn)
                    except:
                        pass
                except Exception as e:
                    err = str(e)
                    if 'The access token being passed has expired' in err:
                        self._reauth()
                    self.quote_err[symbol] += 1
                    self.on_event(dict(symbols=[symbol], type='error', name='tda-quotes', desc=err, source=str(self)))
                time.sleep(1)
            self.quotes_cnt += 1
            time.sleep(self.delay_prices)

    def _news_to_evt(self, news):
        evt = dict(title=news['5'], type='article', source=news['10'], hot=news['9'], symbols=[news['key']])
        if evt['title'] == 'N/A':
            return None
        return evt

    def _reauth(self):
        self.tda.load_login(os.path.join('data', 'tda-login'))