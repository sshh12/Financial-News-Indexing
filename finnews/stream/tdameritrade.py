from collections import defaultdict
from pymeritrade import TDAClient
import pymeritrade.auth as auth
from threading import Thread
from finnews.config import config
from finnews.stream.abs import Stream
import pendulum
import requests
import random
import time
import os


CREDS = config["creds"]["tda"]
CFG = config["watch"]["tda"]


class CustomHandler(auth.SeleniumHeadlessHandler):
    def get_login_creds(self):
        return CREDS["username"], CREDS["password"]

    def get_sms_code(self):
        time.sleep(30)
        # hidden auth method
        code = eval(CREDS["sms_script"])
        print("TDA code", code)
        return code


class StreamTDA(Stream):
    def __init__(self):
        self.tda = TDAClient(CREDS["consumer_key"], auth_handler=CustomHandler)
        self._reauth()
        self.stream = self.tda.create_stream(debug=False)
        self.symbols = CFG.get("stocks", config["symbols_list_all"])
        self.delay_prices = CFG.get("delay_prices", 60 * 60)
        self.warmup_period = CFG.get("warmup", 30)

        self.warmup = True
        self.quotes_cnt = 0
        self.quote_err = defaultdict(lambda: 0)

    def start(self):
        self.quote_thread = Thread(target=self._start_quotes)
        self.quote_thread.start()
        self.stream.start()
        self.stream.subscribe("news", symbols=self.symbols, fields=[0, 5, 9, 10])
        time_start = time.time()
        for stream_data in self.stream.live_data():
            if self.warmup and time.time() - time_start < self.warmup_period:
                # flush old news
                continue
            else:
                self.warmup = False
            for symbol, article in stream_data.data.items():
                evt = self._news_to_evt(symbol, article)
                if evt is not None:
                    self.on_event(evt)

    def _start_quotes(self):
        symbols = list(self.symbols) + ["FUTUREES", "FUTUREGC", "FUTUREBTC", "FUTURECL"]
        while True:
            # shuffle to avoid consistent rate limits on symbols
            random.shuffle(symbols)
            for symbol in symbols:
                if self.quotes_cnt > 10 and self.quote_err[symbol] / self.quotes_cnt > 0.5:
                    continue
                ts = int(pendulum.now().timestamp() * 1000)
                price_fn = os.path.join(config["data_dir"], "watch", "ticks", "P_{}_{}.csv".format(symbol, ts))
                options_fn = os.path.join(config["data_dir"], "watch", "ticks", "O_{}_{}.csv".format(symbol, ts))
                tda_sym = symbol.replace("FUTURE", "/")
                try:
                    self.tda.history(parse_dates=False, span="day", freq="minute", latest=True)[tda_sym].to_csv(
                        price_fn
                    )
                    try:
                        # tbh options data is just extra
                        time.sleep(1)
                        self.tda.options(quotes=True)[tda_sym].to_csv(options_fn)
                    except:
                        pass
                except KeyError:
                    pass
                except Exception as e:
                    err = str(e)
                    if "The access token being passed has expired" in err:
                        self._reauth()
                    self.quote_err[symbol] += 1
                    self.on_event(dict(symbols=[symbol], type="error", name="tda-quotes", desc=err, source=str(self)))
                time.sleep(1)
            self.quotes_cnt += 1
            time.sleep(self.delay_prices)

    def _news_to_evt(self, symbol, article):
        evt = dict(
            title=article["headline"], type="article", source=article["source"], hot=article["is_hot"], symbols=[symbol]
        )
        if evt["title"] == "N/A":
            return None
        return evt

    def _reauth(self):
        login_fn = os.path.join(config["data_dir"], "tda-login")
        self.tda.load_login(login_fn)
        self.tda.save_login(login_fn)

