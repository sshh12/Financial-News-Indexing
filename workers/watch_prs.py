from articles.releases import SCRAPERS
from config import config

import asyncio
import aiohttp
import re


def pr_to_sql_article(article):
    update = {
        'title': article.headline,
        'content': article.content,
        'url': article.url,
        'source': article.source,
        'published': article.date,
        'found': article.found
    }
    return update


async def _fetch_and_log(scrapers, cache, log_new=True):
    async with aiohttp.ClientSession() as session:
        for scrap in scrapers:
            scrap._session = session
        fetch_tasks = [scrap.read_prs() for scrap in scrapers]
        for symbol, prs in await asyncio.gather(*fetch_tasks):
            prs = [pr_to_sql_article(pr) for pr in prs]
            for pr in prs:
                key = (symbol, pr['title'])
                if key not in cache and log_new:
                    print(symbol, pr['title'], pr['url'])
                cache[key] = pr


async def main():

    scrapers = [S() for S in SCRAPERS]
    cache = {}
    first = True

    while True:
        await _fetch_and_log(scrapers, cache, log_new=(not first))
        first = False
        await asyncio.sleep(60)
        


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())