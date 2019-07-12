import pendulum
import hashlib
import time
import re

from . import analyze


USE_TZ = 'UTC'
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
        self.found = pendulum.now().in_tz(USE_TZ)
        self._id = hash_sha1(re.sub(r'[^\w\d]', '', self.source + self.headline).lower())
        self._analyze()

    def _analyze(self):
        self.vader_headline = analyze.score_vader(self.headline)
        self.vader_content = analyze.score_vader(self.content)

    def __repr__(self):
        return '<Article "{}">'.format(self.headline)
        
    def as_dict(self):
        return {
            'source': self.source,
            'headline': self.headline,
            'date': self.date,
            'found': self.found,
            'content': self.content,
            'url': self.url,
            'vader_headline': self.vader_headline,
            'vader_content': self.vader_content
        }


class ArticleScraper:

    async def _get(self, url_part):
        try:
            async with self._session.get(self.url + url_part, headers=HEADERS) as response:
                return await response.text()
        except (ConnectionRefusedError, UnicodeDecodeError):
            return ''



def hash_sha1(text):
    return hashlib.sha1(bytes(text, 'utf-8')).hexdigest()


def clean_html_text(html):
    html = html.replace('&rsquo;', '\'').replace('&lsquo;', '\'')
    html = html.replace('&ldquo;', '"').replace('&rdquo;', '"').replace('&quot;', '"')
    html = html.replace('&amp;', '&')
    html = html.replace('&copy;', '')
    html = html.replace('&nbsp;', ' ')
    html = html.replace('&lt;', '<').replace('&gt;', '>')
    html = html.replace('•', '*')
    html = html.replace('\r', '')
    html = html.replace('—', '-').replace('&ndash;', '-').replace('&mdash;', '-')
    html = html.replace('‘', '\'').replace('’', '\'')
    html = html.replace('“', '').replace('”', '')
    html = re.sub(r'<style[\s\w=":/\.\-,\'!%&+@\|{}\(\);#\?]*>([\s\S]+?)<\/style>', '', html)
    html = re.sub(r'<script[\s\w=":/\.\-,\'!%&+@\|{}\(\);#\?]*>([\s\S]+?)<\/script>', '', html)
    html = re.sub(r'<\w+[\s\w=":/\.\-,\'!%&+@\|#{}\(\);\?]*>', '', html)
    html = re.sub(r'<\/?[\w\-]+>', '', html)
    html = re.sub(r'<!-*[^>]+>', '', html)
    html = re.sub(r'&#[\w\d]+;', '', html)
    html = re.sub(r'\s{3,}', ' ', html)
    return html.strip()


def _timezone_to_offset(date_string):
    return date_string\
        .replace('ET', '-0500')\
        .replace('EST', '-0500')\
        .replace('EDT', '-0400')


def text_to_datetime(html):

    ## https://pendulum.eustace.io/docs/

    text = clean_html_text(html)

    # 2019-04-12T18:12:00Z
    # 2019-06-26T20:20:19.280Z
    # 2019-06-28T20:22:22+00:00
    try:
        return pendulum.parse(text).in_tz(USE_TZ)
    except ValueError:
        pass

    # 2019-07-05T11:32-500
    try:
        parts = text.split('-')
        parts[-1] = '0' + parts[-1]
        return pendulum.parse('-'.join(parts)).in_tz(USE_TZ)
    except (ValueError, IndexError):
        pass

    # June 27, 2019 6:51pm
    # June 18, 2019 10:40am
    try:
        time_text = text.replace('am', 'AM').replace('pm', 'PM')
        return pendulum.from_format(time_text, 'MMMM D, YYYY h:mmA').in_tz(USE_TZ)
    except (ValueError, IndexError):
        pass

    # JUNE 26, 2019 3:01 PM
    try:
        time_text = text.replace('am', 'AM').replace('pm', 'PM')
        return pendulum.from_format(time_text, 'MMMM D, YYYY h:mm A').in_tz(USE_TZ)
    except (ValueError, IndexError):
        pass
    
    # June 27, 2019 11:47 am ET
    # June 26, 2019 4:07 p.m. ET
    try:
        time_text = _timezone_to_offset(text.replace('.', '').replace(',', '').replace('am', 'AM').replace('pm', 'PM'))
        return pendulum.from_format(time_text, 'MMMM D YYYY h:mm A ZZ').in_tz(USE_TZ)
    except (ValueError, IndexError):
        pass

    # Jul 25 2018 6:09 PM EDT
    try:
        time_text = _timezone_to_offset(text.replace('.', '').replace(',', '').replace('am', 'AM').replace('pm', 'PM'))
        return pendulum.from_format(time_text, 'MMM D YYYY h:mm A ZZ').in_tz('UTC')
    except (ValueError, IndexError):
        pass

    # 4 hours ago
    try:
        hours_ago = int(re.search(r'(\d) hours?', text).group(1))
        return pendulum.now().subtract(hours=hours_ago).in_tz('UTC')
    except AttributeError:
        pass

    raise ValueError('Not datetime: ' + text)


def string_contains(text, items):
    text = text.lower()
    for item in items:
        item_lower = item.lower()
        if item_lower in text:
            return True
    return False