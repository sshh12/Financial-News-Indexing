from finnews.articles.abs import ArticleScraper
from finnews.articles.utils import clean_html_text, url_to_n3karticle
import re


TRIM_AT = ["Forward-Looking Statement", "This press release contains"]


class PharmiWeb(ArticleScraper):
    def __init__(self):
        self.url = "https://www.pharmiweb.com"

    async def read_latest_headlines(self):
        index_html = await self._get("/press-releases")
        headlines = []
        for match in re.finditer(r'<a href="(\/press-release\/[^"]+?)">([^<]+?)<', index_html):
            url = self.url + match.group(1)
            headline = clean_html_text(match.group(2))
            headlines.append((url, headline))
        return "pharmiweb", headlines

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
