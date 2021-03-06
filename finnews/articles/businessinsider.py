from finnews.articles.abs import ArticleScraper
from finnews.articles.utils import clean_html_text, string_contains, text_to_datetime
import asyncio
import json
import re


TOPIC_URLS = [
    "/",
    "/news" "/sai",
    "/clusterstock",
    "/transportation",
    "/politics" "/moneygame",
    "/warroom" "/science",
    "/retail",
    "/enterprise",
]

DELETE_TEXT = ["Here's the latest.", "US-specific live updates can be found here."]

IGNORE_TEXT = [
    "<div",
    "data-authors",
    "Read more: ",
    "Read: ",
    "Getty Images",
    "Get the latest",
    "full, the report",
    "takeaways from the report",
    "getting the full report?",
    "The choice is yours.",
    "Business Insider Intelligence",
    "a brand new FREE report",
    "This is an opinion column",
    "Keep reading to see",
    "post has been translated",
    "Subscribe to our newsletter",
    "Source: ",
    "Click here to ",
    "Got a tip?",
    "@businessinsider.com",
    " Join here.",
    "AP Photo",
    "If you are a ",
    "contributed to ",
    "Follow INSIDER on",
    "This is a preview of",
    "For typos, numerical, grammar",
]


class BusinessInsider(ArticleScraper):
    def __init__(self):
        self.url = "https://www.businessinsider.com"

    async def read_article(self, url):

        article_html = await self._get(url)

        headline_match = re.search(r">([^<]+)<\/h1>", article_html)
        if not headline_match:
            return None
        headline = clean_html_text(headline_match.group(1))

        if headline == "Whoops!":
            return None

        date_match = re.search(r'data-timestamp="([\-+\dTZ:]+)"', article_html)
        if not date_match:
            return None
        date = text_to_datetime(date_match.group(1))

        article_match = re.search(r'<script type="application\/ld\+json">([\s\S]+?)<\/script>', article_html)
        if not article_match:
            return None

        article_text = json.loads(article_match.group(1).strip())["articleBody"]
        if ">>" in article_text:
            article_text = article_text[: article_text.index(">>")]
        article_text = re.sub("([a-z])([A-Z])", "\\1. \\2", article_text)
        article_text = re.sub("\.([A-Z])", ". \\1", article_text)
        for dtext in DELETE_TEXT:
            article_text = article_text.replace(dtext, "")
        text = clean_html_text(article_text).split("\n")
        text = [p for p in text if not string_contains(p, IGNORE_TEXT)]

        return ("businessinsider", headline, date, "\n\n\n".join(text), self.url + url)

    async def read_news_list(self, topic_urls, pages=5):

        articles = []

        article_urls = set()
        for url in topic_urls:
            list_html = await self._get(url)
            for match in re.finditer(r'businessinsider.com(\/[^\/&\?="]{8,})"', list_html):
                article_urls.add(match.group(1))

        articles = await asyncio.gather(*[self.read_article(url) for url in article_urls])

        return [article for article in articles if article is not None]

    async def read_news(self):
        return await self.read_news_list(TOPIC_URLS)

    async def read_latest_headlines(self):
        index_html = await self._get("/latest/")
        headlines = []
        for match in re.finditer(r'href="(https:\/\/[\w\.]+businessinsider.com\/news[^"]+?)"\s*>([^<]+?)<', index_html):
            url = match.group(1)
            headline = clean_html_text(match.group(2))
            if len(headline) == 0:
                continue
            headlines.append((url, headline))
        for match in re.finditer(r'href="(\/[^"]+?\d+)"\s*>([^<]+?)<', index_html):
            url = self.url + match.group(1)
            headline = clean_html_text(match.group(2))
            if len(headline) == 0:
                continue
            headlines.append((url, headline))
        return "businessinsider", headlines

