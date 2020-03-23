from . import Article, clean_html_text, ArticleScraper, string_contains
import pendulum

import newspaper
import asyncio
import re
from config import config


SOURCE_SITES = config['news']['newpaper3k']['sources']

IGNORE_LINE_WITH = [
    'Learn more now.',
    'Want to be alerted before Jim Cramer',
    'Check out the rest of the conversation',
    'This story has been updated',
    'please consider joining Slate Plus',
    'usual commenting policies apply',
    'Associated Press, USA TODAY',
    'Fool on!',
    '- Getty Images',
    'Photo illustration by Slate',
    '(Reporting by '
]


class Newspaper3k(ArticleScraper):

    def __init__(self):
        pass

    async def read_source(self, site):
        paper = newspaper.build(site, language='en', memoize_articles=True)
        source = 'newspaper3k-' + site.replace('http://', '').replace('https://', '')
        articles = []
        for i, article in enumerate(paper.articles):
            print(' >', site, i)
            try:
                article.download()
                article.parse()
                assert article.title is not None
                assert article.text is not None
                assert article.publish_date is not None
            except:
                continue
            headline = clean_html_text(article.title)
            text = clean_html_text(article.text)
            text = '\n\n'.join([section for section in text.split('\n\n') 
                if not string_contains(section, IGNORE_LINE_WITH)])
            if len(text) < 30:
                continue
            date = pendulum.instance(article.publish_date)
            articles.append(Article(source, headline, date, text, article.url))
        return articles

    async def read_news(self):
        articles = await asyncio.gather(*[self.read_source(site) for site in SOURCE_SITES])
        all_ = []
        for group in articles:
            all_.extend(group)
        return all_