from . import Article, ArticleScraper, clean_html_text, string_contains, text_to_datetime

import asyncio
import re


IGNORE_TEXT = [
    'This copy is for your personal',
    ' Write to ',
    'Read: ',
    'Read more: ',
    ' All Rights Reserved',
    'barrons.com',
    'dowjones.com',
    'Write to ',
    'Subscribe or Sign In',
    'Barron\'s: ',
    'Find out more'
]


class Barrons(ArticleScraper):

    def __init__(self):
        self.url = 'https://www.barrons.com'

    async def read_article(self, url, parse_headline=True, parse_date=True):

        article_html = await self._get(url)

        text = []
        headline = ''
        date = ''

        if parse_headline:
            headline_match = re.search(r'itemprop="headline">([^<]+)<\/h1>', article_html)
            if not headline_match:
                return None
            headline = clean_html_text(headline_match.group(1))

        if parse_date:
            date_match = re.search(r'(\w+ \d+, \w+ \d+:\d+ \w+ \w+)\s+<\/time>', article_html)
            if not date_match:
                return None
            date = text_to_datetime(date_match.group(1))

        text = []

        for p_match in re.finditer(r'<p>([\s\S]+?)<\/p>', article_html):
            paragraph = clean_html_text(p_match.group(1))
            if len(paragraph) == 0 or string_contains(paragraph, IGNORE_TEXT):
                continue
            text.append(paragraph)

        if len(text) == 0:
            return None

        return Article('barrons', headline, date, '\n\n\n'.join(text), self.url + url)

    async def read_news_list(self, pages=5):

        articles = []
        
        article_urls = set()
        for i in range(1, pages + 1):
            article_ids = set()
            list_html = await self._get('/real-time/{0}?id=%7B%22db%22%3A%22barronsblog%2Cbarrons%22%2C%22query%22%3A%22language%3Den%20NOT%20(subject-value%3A%3D%27BARBRIEF%27%20or%20subject-value%3A%3D%27BARHIDEFEED%27)%22%2C%22page%22%3A%22{0}%22%2C%22count%22%3A20%7D&type=search_collection'.format(i))
            for match in re.finditer(r'id\\?":\\?"([\w\d]+)\\?"', list_html):
                article_ids.add(match.group(1))
            for id_ in article_ids:
                article_data = await self._get('/real-time/{}?id={}&type=article'.format(i, id_))
                url_match = re.search(r'"url\\?":\\?"https:\/\/www.barrons.com(\/articles\/[^"]+)"', article_data)
                if url_match:
                    article_urls.add(url_match.group(1))

        articles = await asyncio.gather(*[self.read_article(url) for url in article_urls])

        return [article for article in articles if article is not None]

    async def read_news(self):
        return await self.read_news_list()

    async def read_latest_headlines(self):
        index_html = await self._get('/real-time?mod=hp_LATEST&mod=hp_LATEST')
        headlines = []
        for match in re.finditer(r'headline-link--[\w\d ]+" href="([^"]+?)">([^<]+?)<', index_html):
            url = match.group(1)
            headline = clean_html_text(match.group(2))
            headlines.append((url, headline))
        return 'barrons', headlines

    async def resolve_url_to_content(self, url):
        art = await self.read_article(url.replace(self.url, ''), 
            parse_headline=False, parse_date=False)
        return art.content
