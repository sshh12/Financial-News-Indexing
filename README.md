# Financial News Indexing

> A suite of market/financial news webscrapers.

### Usage

1. `$ pip install requirements.txt`
2. `$ python finnews\watch.py`

### Config

Use `config.yaml` for most things.

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
  name: "..."
  user: "..."
  password: "..."
  host: "..."
robinhood:
  username: "..."
  password: "..."
slack:
  token: "..."
  channel: "..."
tda:
  consumer_key: "..."
```

### Sources

- TDAmeritrade
- Twitter
- MarketWatch
- SeekingAlpha
- PRNewsWire
- RTTNews
- BusinessWire
- GlobeNewsWire
- AccessWire
- Moodys
- TheStreet
- EarningsCast
- CNN
- PharmiWeb
- Alpha Stock News
- Financial Times
- Barrons
- US Federal Reserve
- US BLS
- FinViz
- Zacks
- StockTwits
- Misc Press Releases
