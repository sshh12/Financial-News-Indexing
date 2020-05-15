import pendulum
import hashlib
import time
import re

from config import config
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

    async def _get(self, url_part, headers=HEADERS):
        try:
            async with self._session.get(self.url + url_part, headers=headers) as response:
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
    html = html.replace('•', '*').replace('●', '* ')
    html = html.replace('\r', '').replace('…', '...')
    html = html.replace('—', '-').replace('&ndash;', '-').replace('&mdash;', '-').replace('ー', '-')
    html = html.replace('‘', '\'').replace('’', '\'')
    html = html.replace('“', '').replace('”', '').replace('»', '>>')
    html = html.replace('✅', '').replace('→', '->').replace('💯', '').replace('🚨', '')
    html = html.replace('Â\xa0', ' ').replace('Â½', '').replace('®', '').replace('\xa0', ' ')
    html = html.replace('™', '').replace('&reg;', '')
    html = re.sub(r'<style[\s\w=":/\.\-,\'!%&+@\|{}\(\);#~\?]*>([\s\S]+?)<\/style>', '', html)
    html = re.sub(r'<script[\s\w=":/\.\-,\'!%&+@\|{}\(\);#~\?]*>([\s\S]+?)<\/script>', '', html)
    html = re.sub(r'<\w+[\s\w=":/\.\-,\'!%&+@\|#~{}\(\);\?]*>', '', html)
    html = re.sub(r'<\/?[\w\-]+>', '', html)
    html = re.sub(r'<!-*[^>]+>', '', html)
    html = re.sub(r'&#[\w\d]+;', '', html)
    html = re.sub(r'\s{3,}', ' ', html)
    html = re.sub(r'https:\/\/t.co\/[\w]+', ' ', html)
    html = re.sub(r'RT @\w+:', '', html)
    html = re.sub('([a-z])\s{2,}([A-Z])', '\\1 \\2', html)
    html = html.replace(' (Updated)', '')
    return html.strip()


def _timezone_to_offset(date_string):
    return date_string\
        .replace('ET', '-0500')\
        .replace('EST', '-0500')\
        .replace('EDT', '-0400')\
        .replace('UTC', '-0000')


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
    # March 24, 2020 at 9:11 a.m. ET
    try:
        time_text = _timezone_to_offset(text.replace(' at ', ' ').replace('.', '')\
            .replace(',', '').replace('am', 'AM').replace('pm', 'PM'))
        return pendulum.from_format(time_text, 'MMMM D YYYY h:mm A ZZ').in_tz(USE_TZ)
    except (ValueError, IndexError):
        pass

    # Jul 5, 2019 12:30 UTC
    try:
        time_text = _timezone_to_offset(text.replace('.', '').replace(',', ''))
        return pendulum.from_format(time_text, 'MMM D YYYY H:mm ZZ').in_tz('UTC')
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

    # Mon Mar 23 16:05:53 +0000 2020
    try:
        return pendulum.from_format(time_text, 'ddd MMM D HH:mm:ss ZZ YYYY').in_tz(USE_TZ)
    except (ValueError, AttributeError):
        pass

    # April 02, 2020
    try:
        time_text = text.replace(',', '')
        return pendulum.from_format(time_text, 'MMMM DD YYYY').in_tz(USE_TZ)
    except (ValueError, AttributeError):
        pass

    # 31 March 2020
    try:
        time_text = text.replace(',', '')
        return pendulum.from_format(time_text, 'DD MMMM YYYY').in_tz(USE_TZ)
    except (ValueError, AttributeError):
        pass

    # 11 Mar. 2020
    try:
        time_text = text.replace(',', '').replace('.', '')
        return pendulum.from_format(time_text, 'DD MMM YYYY').in_tz(USE_TZ)
    except (ValueError, AttributeError):
        pass

    # Apr 7, 2020
    try:
        time_text = text.replace(',', '')
        return pendulum.from_format(time_text, 'MMM D YYYY').in_tz(USE_TZ)
    except (ValueError, AttributeError):
        pass

    # Apr022020
    # Mar 10, 2020
    try:
        time_text = text.replace(',', '').replace(' ', '')
        return pendulum.from_format(time_text, 'MMMDDYYYY').in_tz(USE_TZ)
    except (ValueError, AttributeError):
        pass

    # 03/31/20
    # 03.27 2020
    # 03 27 2020
    try:
        time_text = text.replace('.', ' ').replace('/', '-').replace(' ', '-')
        return pendulum.from_format(time_text, 'MM-DD-YY').in_tz(USE_TZ)
    except (ValueError, AttributeError):
        pass

    raise ValueError('Not datetime: ' + text)


def string_contains(text, items):
    text = text.lower()
    for item in items:
        item_lower = item.lower()
        if item_lower in text:
            return True
    return False


def truncate_sentence(text):
    text_fix = text.replace('U.S.', 'U_S_')
    def first_index(token):
        try:
            return text_fix.index(token, 5)
        except:
            return len(text)
    idx = min([first_index('.'), first_index('?'), first_index('!'), first_index('\n')])
    return text[:idx+1]


def tokenize(text):
    text = re.sub(r'[!\.\?\n\r]', '', text)
    text = re.sub(r'\s{2,}', ' ', text)
    return text.split(' ')


def extract_symbols(text, _token_to_sym={}):
    symbs = set()
    for match in re.finditer(r'\$([A-Z\.]+)\b', text):
        symbs.add(match.group(1))
    for match in re.finditer(r' \(([A-Z\.]+)\)', text):
        symbs.add(match.group(1))
    tokens = tokenize(text)
    if len(_token_to_sym) == 0:
        for sym, kwords in config['keywords']['symbols'].items():
            for kw in kwords:
                _token_to_sym[kw] = sym
    for token in tokens:
        sym = _token_to_sym.get(token)
        if sym is not None:
            symbs.add(sym)
    return symbs