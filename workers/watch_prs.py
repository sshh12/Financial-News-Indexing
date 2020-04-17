from articles.releases import SCRAPERS
from config import config

import pendulum
import asyncio
import aiohttp
import re

import nest_asyncio
nest_asyncio.apply()


def _pr_to_sql_article(article):
    update = {
        'title': article.headline,
        'content': article.content,
        'url': article.url,
        'source': article.source,
        'published': article.date,
        'found': article.found
    }
    return update


def _send_slack(date, symbol, title, url, _cache=[]):
    from slack import WebClient
    if len(_cache) == 0:
        _cache.append(WebClient(token=config['creds']['slack']['token']))
    client = _cache[0]
    msg = '`{}` *{}* {} {}'.format(str(date), symbol, title, url)
    client.chat_postMessage(
        channel=config['creds']['slack']['pr_channel'],
        text=msg)


def _on_new_pr(date, symbol, title, url):
    if 'slack' in config['notify']:
        _send_slack(date, symbol, title, url)
    print(str(date), symbol)
    print(title)
    print(url)
    print('-'*80)


async def poll_prs(scrapers, cache, log_new=True, log_empty=False):
    async with aiohttp.ClientSession() as session:
        for scrap in scrapers:
            scrap._session = session
        fetch_tasks = [scrap.read_prs() for scrap in scrapers]
        for symbol, name, prs in await asyncio.gather(*fetch_tasks):
            prs = [_pr_to_sql_article(pr) for pr in prs]
            if len(prs) == 0 and log_empty:
                print('WARN: nothing found for', name)
            for pr in prs:
                key = (symbol, pr['title'])
                if key not in cache and log_new:
                    _on_new_pr(pendulum.now(), symbol, pr['title'], pr['url'])
                cache[key] = pr


async def main():

    print('Watching...')

    scrapers = [Scraper() for Scraper in SCRAPERS]
    cache = {}
    first = True

    while True:
        await poll_prs(scrapers, cache, log_empty=first, log_new=(not first))
        first = False
        await asyncio.sleep(45)
        


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())