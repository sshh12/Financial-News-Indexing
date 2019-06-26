from datetime import datetime
import re


HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
}


class Article:

    def __init__(self, source, headline, date, content, url):
        self.source = source
        self.headline = headline
        self.date = date
        self.content = content
        self.url = url
        self.found = datetime.now()
        self._id = re.sub(r'[^\w\d]', '', self.source + self.headline).lower()
        
    def as_dict(self):
        return {
            'source': self.source,
            'headline': self.headline,
            'date': self.date,
            'found': self.found,
            'content': self.content,
            'url': self.url
        }


def clean_html_text(html):
    html = html.replace('&rsquo;', '\'')
    html = html.replace('&lsquo;', '\'')
    html = html.replace('&ldquo;', '"')
    html = html.replace('&rdquo;', '"')
    html = html.replace('&amp;', '&')
    html = re.sub(r'&#[\w\d]+;', '', html)
    return html