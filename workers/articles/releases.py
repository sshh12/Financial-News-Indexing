from . import Article, clean_html_text, text_to_datetime, HEADERS

import pendulum
import asyncio
import json
import re


class PRScraper:

    def __init__(self):
        pass

    async def _get(self, url, method='GET', json={}):
        try:
            if method == 'GET':
                async with self._session.get(url, headers=HEADERS) as response:
                    return await response.text()
            elif method == 'POST':
                async with self._session.post(url, headers=HEADERS, json=json) as response:
                    return await response.text()
        except (ConnectionRefusedError, UnicodeDecodeError):
            return ''

    async def read_prs(self):
        raise NotImplementedError()


class RegexPRScraper(PRScraper):

    async def read_prs_with_regex(self, regex, url_path, type_to_group={'date': 1, 'url': 2, 'title': 3}):
        resp = await self._get(self.URL + url_path)
        releases = []
        for match in re.finditer(regex, resp):
            date = text_to_datetime(match.group(type_to_group['date']).strip())
            url = self.URL + match.group(type_to_group['url']).strip()
            title = clean_html_text(match.group(type_to_group['title']))
            releases.append(Article(self.NAME.lower(), title, date, "", url))
        return self.SYMBOL, self.NAME, releases


class GetPressReleaseJSONScraper(PRScraper):

    async def read_prs_from_api(self, path, method='GET', params=None):
        resp = await self._get(self.URL + path, method=method, json=params)
        data = json.loads(resp)['GetPressReleaseListResult']
        releases = []
        for item in data:
            date = text_to_datetime(item['PressReleaseDate'])
            url = self.URL + item['LinkToDetailPage']
            title = clean_html_text(item['Headline'])
            releases.append(Article(self.NAME.lower(), title, date, "", url))
        return self.SYMBOL, self.NAME, releases


class Gilead(RegexPRScraper):

    URL = 'https://www.gilead.com'
    NAME = 'Gilead Sciences'
    SYMBOL = 'GILD'

    async def read_prs(self):
        return await self.read_prs_with_regex(
            r'<p>\s*([\w, ]+)\s*<\/p>\s*<a href="([^"]+)">([^<]+)<\/a>',
            '/news-and-press/press-room/press-releases'
        )


class Kiniksa(RegexPRScraper):

    URL = 'https://investors.kiniksa.com'
    NAME = 'Kiniksa Pharmaceuticals'
    SYMBOL = 'KNSA'

    async def read_prs(self):
        return await self.read_prs_with_regex(
            r'<h3>([/\d]+)<\/h3>\s*<\/div>\s*<div[ clas="\-o\dm]+>\s*<h4>\s*<a href="([^"]+)">([^<]+)<\/a>',
            '/news-events/press-releases'
        )


class Akero(RegexPRScraper):

    URL = 'https://ir.akerotx.com'
    NAME = 'Akero Therapeutics'
    SYMBOL = 'AKRO'

    async def read_prs(self):
        return await self.read_prs_with_regex(
            r'date-time">\s*([\d\-]+)\s*<\/div>\s*<div class="[a-z- ]+">\s*<a href="([^"]+)" hreflang="\w+">([^<]+)<\/a>',
            '/news-events/news-releases'
        )


class Fate(RegexPRScraper):

    URL = 'https://ir.fatetherapeutics.com'
    NAME = 'Fate Therapeutics'
    SYMBOL = 'FATE'

    async def read_prs(self):
        return await self.read_prs_with_regex(
            r'class="datetime">([<>="\w /]+?)<\/time>\s*<\/td>[\s\S]*?<a href="([^"]+)" hreflang="\w+">([^<]+)<\/a>',
            '/press-releases'
        )


class Citius(RegexPRScraper):

    URL = 'https://ir.citiuspharma.com'
    NAME = 'Citius Pharmaceuticals'
    SYMBOL = 'CTXR'

    async def read_prs(self):
        return await self.read_prs_with_regex(
            r'media-heading">\s*<a href="([^"]+)">\s*([^<]+)<\/a>\s*<\/h2>\s*<div class="date"><time datetime="([\d\- :]+)"',
            '/press-releases',
            type_to_group={'date': 3, 'url': 1, 'title': 2}
        )


class Novavax(RegexPRScraper):

    URL = 'http://ir.novavax.com'
    NAME = 'Novavax'
    SYMBOL = 'NVAX'

    async def read_prs(self):
        return await self.read_prs_with_regex(
            r'class="field__item">([\w ,]+)<\/div>[\s\S]+?<h4><a href="([^"]+)" hreflang="\w+">([^<]+)<\/a>',
            '/press-releases'
        )


class CytoDyn(RegexPRScraper):

    URL = 'https://www.cytodyn.com'
    NAME = 'CytoDyn'
    SYMBOL = 'CYDY'

    async def read_prs(self):
        return await self.read_prs_with_regex(
            r'media-heading">\s*<a href="([^"]+)">\s*([^<]+)<\/a>\s*<\/h2>\s*<div class="date"><time datetime="([\d\- :]+)"',
            '/investors/news-events/press-releases',
            type_to_group={'date': 3, 'url': 1, 'title': 2}
        )


class Athersys(GetPressReleaseJSONScraper):

    URL = 'https://www.athersys.com'
    NAME = 'Athersys'
    SYMBOL = 'ATHX'

    async def read_prs(self):
        year = pendulum.now().year
        return await self.read_prs_from_api(
            '/feed/PressRelease.svc/GetPressReleaseList?apiKey=BF185719B0464B3CB809D23926182246' +
            '&LanguageId=1&bodyType=0&pressReleaseDateFilter=3&categoryId=1cb807d2-208f-4bc3-9133-6a9ad45ac3b0' +
            '&pageSize=-1&pageNumber=0&tagList=&includeTags=true&year={}&excludeSelection=1'.format(year))


class Pfizer(GetPressReleaseJSONScraper):

    URL = 'https://investors.pfizer.com'
    NAME = 'Pfizer'
    SYMBOL = 'PFE'

    async def read_prs(self):
        year = pendulum.now().year
        return await self.read_prs_from_api(
            '/Services/PressReleaseService.svc/GetPressReleaseList',
            method='POST',
            params={"serviceDto": 
                {"ViewType":"2", "ViewDate":"", "RevisionNumber":"1", "LanguageId":"1",
                "Signature":"", "ItemCount":-1, "StartIndex":0, "TagList":[], "IncludeTags":True},
                "pressReleaseBodyType":3, "pressReleaseCategoryWorkflowId":
                "00000000-0000-0000-0000-000000000000", "pressReleaseSelection":3,
                "excludeSelection":0, "year": year}
        )


class Immunomedics(RegexPRScraper):

    URL = 'https://www.immunomedics.com'
    NAME = 'Immunomedics'
    SYMBOL = 'IMMU'

    async def read_prs(self):
        year = pendulum.now().year
        return await self.read_prs_with_regex(
            r'<a href="https:\/\/www.immunomedics.com([^"]+)">\s*<div class="row">\s*<h6>([^<]+?)<\/h6>\s*<h5>([^<]+?)<\/h5>',
            '/our-company/news-and-events/{}/'.format(year),
            type_to_group={'date': 2, 'url': 1, 'title': 3}
        )


class EmergentBioSolutions(RegexPRScraper):

    URL = 'https://investors.emergentbiosolutions.com'
    NAME = 'Emergent Bio Solutions'
    SYMBOL = 'EBS'

    async def read_prs(self):
        year = pendulum.now().year
        return await self.read_prs_with_regex(
            r'field-nir-date">([^<]+?)<\/td>[\s\S]+?<a href="([^"]+?)" class="[\w\-]+">([^>]+?)<',
            '/news-releases?field_nir_news_date_value[min]={}'.format(year)
        )


class BioNTech(RegexPRScraper):

    URL = 'https://investors.biontech.de'
    NAME = 'BioNTech'
    SYMBOL = 'BNTX'

    async def read_prs(self):
        return await self.read_prs_with_regex(
            r'field-nir-date">([^<]+?)<\/td>[\s\S]+?<a href="([^"]+?)" class="[\w\-]+">([^>]+?)<',
            '/press-releases'
        )


class Urogen(RegexPRScraper):

    URL = 'https://investors.urogen.com'
    NAME = 'Urogen Pharma Ltd'
    SYMBOL = 'URGN'

    async def read_prs(self):
        return await self.read_prs_with_regex(
            r'date-time">([^<]+?)<\/div>[\s\S]+?<a href="([^"]+?)" hreflang="\w+">([^<]+?)<',
            '/news-releases'
        )


class Inovio(GetPressReleaseJSONScraper):

    URL = 'http://ir.inovio.com'
    NAME = 'Inovio Ltd'
    SYMBOL = 'INO'

    async def read_prs(self):
        year = pendulum.now().year
        return await self.read_prs_from_api(
            '/Services/PressReleaseService.svc/GetPressReleaseList',
            method='POST',
            params={"serviceDto":{
                "ViewType": "2","ViewDate": "","RevisionNumber": "1","LanguageId": "1",
                "Signature": "","ItemCount": -1,"StartIndex": 0,"TagList": [],"IncludeTags":True},
                "pressReleaseCategoryWorkflowId": "1cb807d2-208f-4bc3-9133-6a9ad45ac3b0",
                "pressReleaseBodyType": 0,"pressReleaseSelection": 3,"excludeSelection": 1,"year": year}
        )


class Moderna(RegexPRScraper):

    URL = 'https://investors.modernatx.com'
    NAME = 'Moderna Inc'
    SYMBOL = 'MRNA'

    async def read_prs(self):
        return await self.read_prs_with_regex(
            r'date-time">([^<]+?)<\/div>[\s\S]+?<a href="([^"]+?)" hreflang="\w+">([^<]+?)<',
            '/news-releases'
        )


class Moleculin(RegexPRScraper):

    URL = 'https://ir.moleculin.com'
    NAME = 'Moleculin Biotech'
    SYMBOL = 'MBRX'

    async def read_prs(self):
        return await self.read_prs_with_regex(
            r'media-heading">\s*<a href="([^"]+)">\s*([^<]+)<\/a>\s*<\/h2>\s*<div class="date"><time datetime="([\d\- :]+)"',
            '/press-releases',
            type_to_group={'date': 3, 'url': 1, 'title': 2}
        )


SCRAPERS = [
    Gilead,
    Kiniksa,
    Akero,
    Fate,
    Citius,
    Novavax,
    CytoDyn,
    Athersys,
    Pfizer,
    Immunomedics,
    BioNTech,
    Urogen,
    Inovio,
    Moderna,
    Moleculin
]