from finnews.articles.abs import ArticleScraper
from finnews.articles.utils import clean_html_text, url_to_n3karticle
import re


class IBTimes(ArticleScraper):
    def __init__(self):
        self.url = "https://www.ibtimes.com"

    async def read_latest_headlines(self):
        index_html = await self._get("/")
        headlines = []
        for match in re.finditer(
            r'<div class="title"><a href="(\/[\w\-]+?)">([^<]+?)<\/a><\/div>\s*<\/article>', index_html
        ):
            url = self.url + match.group(1)
            headline = clean_html_text(match.group(2))
            headlines.append((url, headline))
        return "ibtimes", headlines

    async def resolve_url_to_content(self, url):
        if not url.startswith(self.url):
            return None
        art = url_to_n3karticle(url)
        text = clean_html_text(art.text)
        filtered_text = "\n".join([line for line in text.split("\n") if not line.startswith("Photo:")])
        return filtered_text
