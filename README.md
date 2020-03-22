# Financial News Indexing

> A suite of market/financial news webscrapers.

### Usage

1. Install [Elastic Search](https://www.elastic.co/) on `localhost`
2. `$ pip install requirements.txt`
3. Run with [cron](https://en.wikipedia.org/wiki/Cron) using something like:
```
0 0,4,8,12,14,16,20 * * * sudo python3 /projects/Financial-News-Indexing/workers/fetch_news.py >> /projects/log.txt 2>&1
0 0,2,4,6,8,12,14,16,18,20 * * * sudo python3 /projects/Financial-News-Indexing/workers/fetch_prices.py >> /projects/log.txt 2>&1
0 0,4,8,12,14,16,20 * * * sudo python3 /projects/Financial-News-Indexing/workers/fetch_meta.py >> /projects/log.txt 2>&1
```

<img width="827" alt="chrome_2020-03-18_11-15-24" src="https://user-images.githubusercontent.com/6625384/76982365-c80ae200-6909-11ea-8704-b496434e1b3e.png">

### Config
See `workers.yaml`

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
* Misc in Newspaper3k