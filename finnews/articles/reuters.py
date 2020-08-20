from finnews.articles.abs import ArticleScraper
from finnews.articles.utils import clean_html_text, text_to_datetime
import asyncio
import re


TOPIC_URLS = [
    "businessnews",
    "marketsNews",
    "technologynews",
    "healthnews",
    "banks",
    "aerospace-defense",
    "innovationintellectualproperty",
    "environmentnews",
    "worldnews",
    "esgnews",
]


class Reuters(ArticleScraper):
    def __init__(self):
        self.url = "https://www.reuters.com"

    async def read_article(self, url, parse_headline=True, parse_date=True):

        article_html = await self._get(url)

        text = []
        headline = ""
        date = ""

        if parse_headline or parse_date:
            date_match = re.search(r"(\w+ \d+, \d{4}) \/\s+(\d+:\d+ \w+) ", article_html)
            headline_match = re.search(r'ArticleHeader_headline">([^<]+)<\/h1>', article_html)
            if not date_match or not headline_match:
                return None
            headline = clean_html_text(headline_match.group(1))
            date = text_to_datetime(date_match.group(1) + " " + date_match.group(2))

        start_idx = article_html.index("StandardArticleBody_body")
        try:
            end_idx = article_html.index("Attribution_container")
        except ValueError:
            end_idx = len(article_html)
        content_html = article_html[start_idx:end_idx]
        for paragraph_match in re.finditer(r"<p>([^<]+)<\/p>", content_html):
            paragraph = clean_html_text(paragraph_match.group(1))
            if paragraph.count(" ") > 1:
                text.append(paragraph)

        if len(text) == 0:
            return None

        return ("reuters", headline, date, "\n\n\n".join(text), self.url + url)

    async def read_news_list(self, topics):

        articles = []

        article_urls = set()
        for topic_url in topics:
            list_html = await self._get("/news/archive/{}?view=page&page=1&pageSize=10".format(topic_url))
            for match in re.finditer(r'href="(\/article\/[^"]+)"', list_html):
                article_urls.add(match.group(1))

        articles = await asyncio.gather(*[self.read_article(url) for url in article_urls])

        return [article for article in articles if article is not None]

    async def read_news(self):
        return await self.read_news_list(TOPIC_URLS)

    async def read_latest_headlines(self):
        index_html = await self._get("/finance/markets")
        headlines = []
        for match in re.finditer(r'href="([^"]+?)">\s*?<h3 class="story-title">\s*([^<]+?)<', index_html):
            url = self.url + match.group(1)
            headline = clean_html_text(match.group(2))
            headline = re.sub(r"([A-Z])-([A-Z])", "\\1 - \\2", headline)
            headlines.append((url, headline))
        return "reuters", headlines

    async def resolve_url_to_content(self, url):
        art = await self.read_article(url.replace(self.url, ""), parse_headline=False, parse_date=False)
        if art is None:
            return None
        return art[3]
