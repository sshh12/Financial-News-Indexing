from finnews.articles.abs import ArticleScraper
from finnews.articles.utils import clean_html_text
import re


class RTTNews(ArticleScraper):
    def __init__(self):
        self.url = "https://www.rttnews.com"

    async def read_latest_headlines(self):
        index_html = await self._get("/Content/RTTHeadlines.aspx")
        headlines = []
        for match in re.finditer(r'class="headline">[\s\S]+?<\/span>([^<]+?)<', index_html):
            url = self.url
            headline = clean_html_text(match.group(1))
            headline = re.sub(r"\s{2,}", " ", headline)
            headlines.append((url, headline))
        return "rtt", headlines
