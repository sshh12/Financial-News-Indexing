# Financial News Indexing

> A suite of market/financial news webscrapers.

### PostgreSQL Usage

1. Install [PostgreSQL](https://www.postgresql.org/download/)
2. `$ pip install requirements.txt`
3. Run with [cron](https://en.wikipedia.org/wiki/Cron) using something like:
```
0 0,4,8,12,14,16,20 * * * sudo python3 /projects/Financial-News-Indexing/workers/sql_news.py >> /projects/log.txt 2>&1
0 0,2,4,6,8,12,14,16,18,20 * * * sudo python3 /projects/Financial-News-Indexing/workers/sql_prices.py >> /projects/log.txt 2>&1
```

### Elastic Search Usage

1. Install [Elastic Search](https://www.elastic.co/) on `localhost`
2. `$ pip install requirements.txt`
3. Run with [cron](https://en.wikipedia.org/wiki/Cron) using something like:
```
0 0,4,8,12,14,16,20 * * * sudo python3 /projects/Financial-News-Indexing/workers/es_news.py >> /projects/log.txt 2>&1
0 0,2,4,6,8,12,14,16,18,20 * * * sudo python3 /projects/Financial-News-Indexing/workers/es_prices.py >> /projects/log.txt 2>&1
```

<img width="827" alt="chrome_2020-03-18_11-15-24" src="https://user-images.githubusercontent.com/6625384/76982365-c80ae200-6909-11ea-8704-b496434e1b3e.png">

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
```

### Sources
* Alphavantage
* Crypto Compare
* Financial Modeling Prep
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
* Twitter
* Misc in Newspaper3k