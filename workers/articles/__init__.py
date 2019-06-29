from datetime import datetime, timedelta
import hashlib
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
        self._id = hash_sha1(re.sub(r'[^\w\d]', '', self.source + self.headline).lower())

    def __repr__(self):
        return '<Article "{}">'.format(self.headline)
        
    def as_dict(self):
        return {
            'source': self.source,
            'headline': self.headline,
            'date': self.date,
            'found': self.found,
            'content': self.content,
            'url': self.url
        }


def hash_sha1(text):
    return hashlib.sha1(bytes(text, 'utf-8')).hexdigest()


def clean_html_text(html):
    html = html.replace('&rsquo;', '\'').replace('&lsquo;', '\'')
    html = html.replace('&ldquo;', '"').replace('&rdquo;', '"').replace('&quot;', '"')
    html = html.replace('&amp;', '&')
    html = html.replace('&copy;', '')
    html = html.replace('&nbsp;', ' ')
    html = html.replace('&lt;', '<').replace('&gt;', '>')
    html = html.replace('\r', '')
    html = html.replace('—', '-')
    html = html.replace('‘', '\'').replace('’', '\'')
    html = html.replace('“', '').replace('”', '')
    html = re.sub(r'<style[\s\w=":/\.\-,\'!%&+@{}\(\);#\?]*>([\s\S]+?)<\/style>', '', html)
    html = re.sub(r'<script[\s\w=":/\.\-,\'!%&+@{}\(\);#\?]*>([\s\S]+?)<\/script>', '', html)
    html = re.sub(r'<\w+[\s\w=":/\.\-,\'!%&+@#{}\(\);\?]*>', '', html)
    html = re.sub(r'<\/?\w+>', '', html)
    html = re.sub(r'<!-*[^>]+>', '', html)
    html = re.sub(r'&#[\w\d]+;', '', html)
    html = re.sub(r'\s{3,}', ' ', html)
    return html.strip()


def text_to_datetime(html):

    ## https://docs.python.org/3/library/datetime.html

    text = clean_html_text(html)

    # 2019-04-12T18:12:00Z
    try:
        return datetime.strptime(text, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        pass

    # 2019-06-26T20:20:19.280Z
    try:
        return datetime.strptime(text, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        pass

    # 2019-06-27T07:57:18-04:00
    try:
        timestamp = text.split('-')
        timestamp[-1] = timestamp[-1].replace(':', '')
        return datetime.strptime('-'.join(timestamp), "%Y-%m-%dT%H:%M:%S%z")
    except ValueError:
        pass

    # June 27, 2019 6:51pm
    try:
        timestamp = text.split(' ')
        if len(timestamp[1]) == 2:
            timestamp[1] = '0' + timestamp[1]
        if len(timestamp[3]) == 4:
            timestamp[3] = '0' + timestamp[3]
        return datetime.strptime(' '.join(timestamp), '%B %d, %Y %I:%M%p')
    except (ValueError, IndexError):
        pass

    # JUNE 26, 2019 3:01 PM
    try:
        timestamp = text.split(' ')
        if len(timestamp[1]) == 2:
            timestamp[1] = '0' + timestamp[1]
        if len(timestamp[3]) == 4:
            timestamp[3] = '0' + timestamp[3]
        return datetime.strptime(' '.join(timestamp), '%B %d, %Y %I:%M %p')
    except (ValueError, IndexError):
        pass
    
    # June 27, 2019 11:47 am ET
    # June 26, 2019 4:07 p.m. ET
    try:
        timestamp = text.replace('.', '').replace(',', '').split(' ')
        if len(timestamp[1]) == 1:
            timestamp[1] = '0' + timestamp[1]
        if len(timestamp[3]) == 4:
            timestamp[3] = '0' + timestamp[3]
        timestamp[4] = timestamp[4].upper()
        timestamp[5] = timestamp[5].replace('ET', '-0500').replace('EDT', '-0400')
        return datetime.strptime(' '.join(timestamp), '%B %d %Y %I:%M %p %z')
    except (ValueError, IndexError):
        pass

    # Jul 25 2018 6:09 PM EDT
    try:
        timestamp = text.replace('.', '').replace(',', '').split(' ')
        if len(timestamp[1]) == 1:
            timestamp[1] = '0' + timestamp[1]
        if len(timestamp[3]) == 4:
            timestamp[3] = '0' + timestamp[3]
        timestamp[4] = timestamp[4].upper()
        timestamp[5] = timestamp[5].replace('ET', '-0500').replace('EDT', '-0400')
        return datetime.strptime(' '.join(timestamp), '%b %d %Y %I:%M %p %z')
    except (ValueError, IndexError):
        pass

    # 4 hours ago
    try:
        hours_ago = int(re.search(r'(\d) hours?', text).group(1))
        return datetime.now() - timedelta(hours=hours_ago)
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