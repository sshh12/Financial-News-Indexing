from finnews.articles.abs import ArticleScraper
from finnews.articles.utils import clean_html_text, url_to_n3karticle
import re


class StreetInsider(ArticleScraper):
    def __init__(self):
        self.url = "https://www.streetinsider.com"

    async def read_latest_headlines(self):
        index_html = await self._get("/")
        headlines = []
        for match in re.finditer(r'a href="([A-Z][^"]+?.html)">([^<]+?)<', index_html):
            url = self.url + "/" + match.group(1)
            headline = clean_html_text(match.group(2))
            headlines.append((url, headline))
        return "streetinsider", headlines

    async def resolve_url_to_content(self, url):
        html = await self._get(url.replace(self.url, ""))
        art = url_to_n3karticle(url, input_html=html)
        text = clean_html_text(art.text)
        return text
