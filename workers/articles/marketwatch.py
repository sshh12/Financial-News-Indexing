from . import Article, clean_html_text, ArticleScraper, text_to_datetime, string_contains

import asyncio
import re


IGNORE_TEXT = [
    'Read:',
    'Now read:',
    'See:',
    'And see:',
    'Read more:',
    'Check out:',
    'Related: ',
    'An expanded version of this',
    'Also:',
    'See now:',
    'Don\'t miss:',
    'See also:',
    'For more news:',
    'Full coverage at ',
    'Additional reporting by ',
    'Sign up for ',
    'This story has ',
    'contributed to this',
    'Read this:',
    'This report originally',
    'click on this',
    'you understand and agree that we',
    'Recommended:',
    'Related:',
    'is a MarketWatch reporter',
    ' reporter for MarketWatch.',
    'Follow MarketWatch on ',
    'is an editor for MarketWatch',
    ' is MarketWatch\'s '
]


class MarketWatch(ArticleScraper):

    def __init__(self):
        self.url = 'https://www.marketwatch.com'

    async def read_article(self, url):
        
        article_html = await self._get(url)

        headline_match = re.search(r'itemprop="headline">([\s\S]+?)<\/h1>', article_html)
        if not headline_match:
            return None
        headline = clean_html_text(headline_match.group(1))

        date_match = re.search(r'Published: ([^<]+?)<\/time>', article_html)
        if not date_match:
            return None
        date = text_to_datetime(date_match.group(1))

        text = []

        start_idx = article_html.index('articleBody')
        try:
            end_idx = article_html.index('author-commentPromo')
        except ValueError:
            end_idx = len(article_html)
        content_html = article_html[start_idx:end_idx]
        for paragraph_match in re.finditer(r'<p>([\s\S]+?)<\/p>', content_html):
            p = clean_html_text(paragraph_match.group(1))
            if len(p) >= 30 and not string_contains(p, IGNORE_TEXT):
                text.append(p)

        return Article('marketwatch', headline, date, '\n\n\n'.join(text), self.url + url)

    async def read_news_list(self, iters=10):

        articles = []

        article_urls = set()

        msg_num = None
        channel_id = re.search(r'data-channel-id="([\-\w]+)"', await self._get('/latest-news'))
        if not channel_id:
            return articles
        channel_id = channel_id.group(1)

        for _ in range(iters):

            if msg_num is None:
                list_html = await self._get('/latest-news?position=1.1&partial=true&channelId={}'.format(channel_id))
                msg_num = 9e9
            else:
                list_html = await self._get('/latest-news?position=1.1&partial=true&channelId={}&messageNumber={}'.format(channel_id, msg_num))

            for match in re.finditer(r'href="https:\/\/www.marketwatch.com(\/story[^"]+)"', list_html):
                article_urls.add(match.group(1))

            for match in re.finditer(r'data-msgid="(\d+)"', list_html):
                msg_num = min(int(match.group(1)), msg_num)

            msg_num = msg_num - 20

        articles = await asyncio.gather(*[self.read_article(url) for url in article_urls])

        return [article for article in articles if article is not None]

    async def read_news(self):
        return await self.read_news_list()
