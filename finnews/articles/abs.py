HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"
}


class ArticleScraper:
    async def _get(self, url_part, site=None, headers=HEADERS):
        if site is None:
            site = self.url
        try:
            async with self._session.get(site + url_part, headers=headers) as response:
                return await response.text()
        except (ConnectionRefusedError, UnicodeDecodeError):
            return ""

    async def _post_json(self, url_part, headers=HEADERS, json=None):
        try:
            async with self._session.post(self.url + url_part, headers=headers, json=json) as response:
                return await response.text()
        except (ConnectionRefusedError, UnicodeDecodeError):
            return ""

    async def read_latest_headlines(self):
        return "unk", []

    async def resolve_url_to_content(self, url):
        return None
