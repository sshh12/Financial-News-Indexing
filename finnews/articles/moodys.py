from finnews.articles.abs import ArticleScraper
from finnews.articles.utils import clean_html_text
import re


HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9,la;q=0.8",
    "cache-control": "no-cache",
    "upgrade-insecure-requests": "1",
    "pragma": "no-cache",
}


class Moodys(ArticleScraper):
    def __init__(self):
        self.url = "https://www.moodys.com"

    async def read_latest_headlines(self):
        index_html = await self._get(
            "/researchandratings/research-type/ratings-news/-/00300E/00300E/-/-1/0/-/0/-/-/-/-/-/-/-/-/global/pdf/-/rra",
            headers=HEADERS,
        )
        headlines = []
        for match in re.finditer(r"_href=\'([^\']+?)\' target=\'_self\'>([^<]+)<[\s\S]+?\d+\'>([^<]+?)<", index_html):
            url = self.url + match.group(1)
            headline = clean_html_text(match.group(3) + " -- " + match.group(2))
            headlines.append((url, headline))
        return "moodys", headlines
