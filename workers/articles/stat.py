from . import Article, clean_html_text, ArticleScraper
import re


HEADLINE_REGEX = r'<a href="(https:\/\/www.statnews.com[^"]+?)"[ targe="lcspo\-ink]+?>([^<]+)<'


class STAT(ArticleScraper):

    def __init__(self):
        self.url = 'https://www.statnews.com'

    async def read_latest_headlines(self):
        index_html = await self._get('/latest/')
        headlines = []
        for match in re.finditer(HEADLINE_REGEX, index_html):
            url = match.group(1)
            if '/page/' in url:
                continue
            headline = clean_html_text(match.group(2))
            headlines.append((url, headline))
        return 'stat', headlines
