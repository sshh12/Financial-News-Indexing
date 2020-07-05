from . import Article, clean_html_text, ArticleScraper, string_contains, text_to_datetime, url_to_n3karticle
import asyncio
import json
import re


IGNORE_TEXT = [
    '<span',
    '<svg',
    '<input',
    'No matching results',
    'Tip: ',
    '<a',
    'Give feedback on',
    'Check out our'
    'WATCH: ',
    'SEE ALSO: '
    'has a disclosure policy',
    'More From ',
    'Image source: ',
    '©',
    'Benzinga.com',
    'See more from ',
    'Latest Ratings for ',
    'Stock Analysis Report',
    'To read this article',
    'Want the latest recommendations',
    'See This Ticker',
    'Data source:',
    'Reporting by ',
    'Check Out: '
    'Watch the full ',
    'Follow her on Twitter',
    'View our latest ',
    'Read the latest stocks',
    'Follow Yahoo Finance on',
    'Follow him on ',
    'Read the latest ',
    '[See Also: ',
    'Find live stock market quotes',
    'For tutorials and information',
    'Read more: ',
    '(Updates with ',
    'For more articles like this',
    'Subscribe now to stay ahead'
]


class Yahoo(ArticleScraper):

    def __init__(self):
        self.url = 'https://finance.yahoo.com'

    async def read_article(self, url, parse_headline=True, parse_date=True):
        
        article_html = await self._get(url)

        text = []
        headline = ''
        date = ''
        
        if parse_headline:
            headline_match = re.search(r'>([^<]+)<\/h1>', article_html)
            if not headline_match:
                return None
            headline = clean_html_text(headline_match.group(1))

        if parse_date:
            date_match = re.search(r'datetime="([\d\-T:Z\.]+)" itemprop="datePublished"', article_html)
            if date_match:
                date = text_to_datetime(date_match.group(1))
            else:
                return None

        for p_match in re.finditer(r'<(span|p) [^>]+>([\s\S]+?)<\/(span|p)>', article_html):
            paragraph = clean_html_text(p_match.group(2))
            if paragraph.count(' ') <= 2 or string_contains(paragraph, IGNORE_TEXT) or paragraph[0] == ')':
                continue
            if 'list is empty' in paragraph:
                break
            text.append(paragraph)

        if len(text) == 0:
            return None

        return Article('yahoo', headline, date, '\n\n\n'.join(text), self.url + url)

    async def read_news_list(self):

        articles = []
        
        article_urls = set()
        list_html = await self._get('/rss/topstories')
        for match in re.finditer(r'finance.yahoo.com(\/news\/[\w\-]+.html)', list_html):
            article_urls.add(match.group(1))

        articles = await asyncio.gather(*[self.read_article(url) for url in article_urls])

        return [article for article in articles if article is not None]

    async def read_news(self):
        return await self.read_news_list()

    async def read_latest_headlines(self):
        headlines = []
        urls = set()
        index_html = await self._get('/topic/stock-market-news')
        for match in re.finditer(r'"url":"([^"]+?)",[",\w:]+?"title":"([^"]+?)"', index_html):
            url = match.group(1).replace(r'\u002F', '/')
            if url in urls:
                continue
            else:
                urls.add(url)
            headline = clean_html_text(match.group(2))
            headlines.append((url, headline))
        for kterm in ['Edited Transcript of', 'StreetEvents', 'Bloomberg', 'Zacks']:
            term_resp = await self._get('/v1/finance/search?q={}&lang=en-US&region=US&quotesCount=6&newsCount=4' 
                + '&enableFuzzyQuery=false&quotesQueryId=tss_match_phrase_query' 
                + '&multiQuoteQueryId=multi_quote_single_token_query&newsQueryId=news_cie_vespa' 
                + '&enableCb=true&enableNavLinks=true&enableEnhancedTrivialQuery=true'.format(kterm), site='https://query1.finance.yahoo.com')
            try:
                term_json = json.loads(term_resp)
                for item in term_json['news']:
                    url = item['link']
                    if url in urls:
                        continue
                    else:
                        urls.add(url)
                    headline = clean_html_text(item['title'])
                    headlines.append((url, headline))
            except ValueError:
                pass
        return 'yahoo', headlines

    async def resolve_url_to_content(self, url):
        if not url.startswith(self.url):
            return None
        art = url_to_n3karticle(url)
        text = clean_html_text(art.text)
        if len(text) < 100:
            return None
        return text
