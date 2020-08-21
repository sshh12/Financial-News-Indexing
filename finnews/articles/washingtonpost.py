from finnews.articles.abs import ArticleScraper
from finnews.articles.utils import clean_html_text, url_to_n3karticle
import re

PAGES = ["/business/", "/business/technology/" "/world/"]


class WashingtonPost(ArticleScraper):
    def __init__(self):
        self.url = "https://www.washingtonpost.com"

    async def read_latest_headlines(self):
        used_urls = set()
        headlines = []
        for page in PAGES:
            html = await self._get(page)
            for match in re.finditer(
                r'<a class="" href="(https[^"]+?)" hreflang="en" data-pb-field="headlines.basic"[^>]+?>([^<]+?)<', html
            ):
                url = match.group(1)
                if url in used_urls:
                    continue
                used_urls.add(url)
                headline = clean_html_text(match.group(2))
                headlines.append((url, headline))
        return "washingtonpost", headlines

    async def resolve_url_to_content(self, url):
        if not url.startswith(self.url):
            return None
        art = url_to_n3karticle(url)
        text = clean_html_text(art.text)
        filtered_text = "\n".join([line for line in text.split("\n") if not line.strip().endswith("AD")])
        return filtered_text
