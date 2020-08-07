from finnews.articles.abs import ArticleScraper
from finnews.articles.utils import clean_html_text, url_to_n3karticle
import re


TRIM_AT = [
    "About ResearchAndMarkets.com",
    "MEDIA CONTACTS:",
    "Forward-Looking Statements",
    "Media Contact Information:",
    "CONTACT:",
    "END\n",
]


class PRNewsWire(ArticleScraper):
    def __init__(self):
        self.url = "https://www.prnewswire.com"

    async def read_latest_headlines(self):
        index_html = await self._get("/news-releases/news-releases-list/")
        headlines = []
        for match in re.finditer(r'news-release" href="([^"]+?)" title="[^"]*?">([^<]+?)<', index_html):
            url = self.url + match.group(1)
            headline = clean_html_text(match.group(2))
            headlines.append((url, headline))
        return "prnewswire", headlines

    async def resolve_url_to_content(self, url):
        art = url_to_n3karticle(url)
        text = clean_html_text(art.text)
        if len(text) < 100:
            return None
        for trim_token in TRIM_AT:
            try:
                idx = text.index(trim_token)
            except:
                continue
            text = text[:idx].strip()
        return text
