# Financial News Indexing

> A suite of market/financial news webscrapers.

### Usage

1. `$ pip install requirements.txt`
2. `$ python workers\watch.py`

### Config
See `config.yaml` for most things.

and create a `creds.yaml` that is formatted like:

```yaml
alphavantage:
    api_keys: 
        - ...
twitter:
    consumer_key: ...
    consumer_secret: ...
    access_token_key: ...
    access_token_secret: ...
postgres:
    name: '...'
    user: '...'
    password: '...'
    host: '...'
robinhood:
    username: '...'
    password: '...'
slack:
    token: '...'
    channel: '...'
tda:
    consumer_key: '...'
```

### Sources

#### Streaming

* TDAmeritrade
* Twitter
* MarketWatch
* SeekingAlpha
* PRNewsWire
* RTTNews
* BusinessWire
* GlobeNewsWire
* AccessWire
* Moodys
* TheStreet
* EarningsCast
* CNN
* PharmiWeb
* Alpha Stock News
* Financial Times
* Barrons
* US Federal Reserve
* US BLS
* FinViz
* Zacks
* StockTwits
* Misc Press Releases

#### Prices
* Alphavantage
* Crypto Compare

#### Articles
* Barrons
* Benzinga
* Bloomberg
* Business Insider
* CNBC
* CNN
* Coin Desk
* IB Times
* Market Watch
* Reuters
* Seeking Alpha
* The Street
* Verge
* Washington Post
* Yahoo
* Misc from Newspaper3k

#### Stats
* Financial Modeling Prep
* Robinhood