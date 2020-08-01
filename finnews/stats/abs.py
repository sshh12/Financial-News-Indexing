HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"
}


class MetaDataSource:
    async def _get(self, url_part):
        try:
            async with self._session.get(self.url + url_part, headers=HEADERS) as response:
                return await response.text()
        except (ConnectionRefusedError, UnicodeDecodeError):
            return ""

    async def read_ratings(self):
        return []

    async def read_lists(self):
        return []

    async def read_group_stats(self):
        return []
