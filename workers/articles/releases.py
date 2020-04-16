from . import Article, clean_html_text, text_to_datetime, HEADERS

import pendulum
import asyncio
import aiohttp
import json
import re


class PRScraper:

    def __init__(self, url=None):
        if url is None:
            self._url = self.URL
        else:
            self._url = url

    async def _get(self, url, method='GET', json_params=None, form_params=None):
        kwargs = {'headers': HEADERS}
        if json_params is not None:
            kwargs['json'] = json_params
        elif form_params is not None:
            kwargs['data'] = form_params
        try:
            if method == 'GET':
                async with self._session.get(url, **kwargs) as response:
                    text = await response.text()
            elif method == 'POST':
                async with self._session.post(url, **kwargs) as response:
                    text = await response.text()
            return text
        except (ConnectionRefusedError, UnicodeDecodeError, aiohttp.client_exceptions.ClientOSError):
            return ''

    async def read_prs(self):
        raise NotImplementedError()


class RegexPRScraper(PRScraper):

    async def read_prs_with_regex(self, regex, url_path, \
            type_to_group={'date': 1, 'url': 2, 'title': 3}, \
            full_url_path=False, article_url_base=None, **kwargs):
        req_url = self._url + url_path
        if full_url_path:
            req_url = url_path
        resp = await self._get(req_url, **kwargs)
        releases = []
        for match in re.finditer(regex, resp):
            date = text_to_datetime(match.group(type_to_group['date']).strip())
            if article_url_base is None:
                url = self._url + match.group(type_to_group['url']).strip()
            else:
                url = article_url_base + match.group(type_to_group['url']).strip()
            title = clean_html_text(match.group(type_to_group['title']))
            if len(title) == 0:
                continue
            releases.append(Article(self.NAME.lower(), title, date, "", url))
        return self.SYMBOL, self.NAME, releases


class GetPressReleaseJSONScraper(PRScraper):

    async def read_prs_from_api(self, path, method='GET', params=None):
        releases = []
        try:
            resp = await self._get(self._url + path, method=method, json_params=params)
            data = json.loads(resp)['GetPressReleaseListResult']
        except:
            return self.SYMBOL, self.NAME, releases
        for item in data:
            date = text_to_datetime(item['PressReleaseDate'])
            url = self._url + item['LinkToDetailPage']
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


class SCWORX(RegexPRScraper):

    URL = 'https://ir.scworx.com'
    NAME = 'SC WORX'
    SYMBOL = 'WORX'

    async def read_prs(self):
        return await self.read_prs_with_regex(
            r'datetime="([\-\d :]+)">[\s\S]+?<a href="https:\/\/ir.scworx.com([^"]+)">([^<]+)<',
            '/press-releases',
        )


class Agenus(RegexPRScraper):

    URL = 'https://investor.agenusbio.com'
    NAME = 'Agenus'
    SYMBOL = 'AGEN'

    async def read_prs(self):
        return await self.read_prs_with_regex(
            r'"wd_date">([^<]+?)<\/div>\s*<div class="wd_title"><a href="https:\/\/investor.agenusbio.com([^"]+?)">([^<]+?)<\/a>',
            '/press-releases?l=5',
        )


class ImmunoTech(RegexPRScraper):

    URL = 'https://aimimmuno.com'
    NAME = 'ImmunoTech'
    SYMBOL = 'AIM'

    async def read_prs(self):
        params = '?b=2265&api=L4g4P2Y7S4&s=0&i=10&g=980&out=0&p=1&n=2&tl=0&sd=1&a=2&rss=1'
        return await self.read_prs_with_regex(
            r'HeadLinesDateCell">([^<]+?)<\/td[\s\S]+?https:\/\/aimimmuno.irpass.com([^"]+?)" title="([^"]+?)">',
            'https://www.b2i.us/b2i/LibraryFeed.asp' + params,
            full_url_path=True, 
            article_url_base='https://aimimmuno.irpass.com',
            method='POST'
        )


class Aldeyra(RegexPRScraper):

    URL = 'https://ir.aldeyra.com'
    NAME = 'Aldeyra Therapeutics'
    SYMBOL = 'ALDX'

    async def read_prs(self):
        return await self.read_prs_with_regex(
            r'date-time">\s*([\w, \d\-]+)\s*<\/div>\s*<div class="[a-z- ]+">\s*<a href="([^"]+)" hreflang="\w+">([^<]+)<\/a>',
            '/press-releases'
        )


class Altimmune(RegexPRScraper):

    URL = 'https://ir.altimmune.com'
    NAME = 'Altimmune'
    SYMBOL = 'ALT'

    async def read_prs(self):
        return await self.read_prs_with_regex(
            r'date-time">\s*([\w, \d\-]+)\s*<\/div>[\s\S]+?<a href="([^"]+)" hreflang="\w+">([^<]+)<\/a>',
            '/investors/press-releases'
        )


class Amgen(RegexPRScraper):

    URL = 'http://investors.amgen.com'
    NAME = 'Amgen'
    SYMBOL = 'AMGN'

    async def read_prs(self):
        return await self.read_prs_with_regex(
            r'article-date">\s*([\w,/ \d\-]+)\s*<\/h3>[\s\S]+?<a href="([^"]+)" hreflang="\w+">([^<]+)<\/a>',
            '/press-releases'
        )


class AppliedDNASciences(RegexPRScraper):

    URL = 'https://adnas.com'
    NAME = 'Applied DNA Sciences'
    SYMBOL = 'APDN'

    async def read_prs(self):
        meta_resp = await self._get(self._url + '/press-releases/')
        nonce_match = re.search(r'data-vc-public-nonce="([^"]+?)"', meta_resp)
        if not nonce_match:
            return []
        nonce = nonce_match.group(1)
        return await self.read_prs_with_regex(
            r'>([^<]+?)<\/h5>[\S\s]+?>([^<]+)<\/h6>[\s\S]+?https:\/\/adnas.com([^"]+?)"',
            '/wp-admin/admin-ajax.php',
            type_to_group={'date': 2, 'url': 3, 'title': 1},
            method='POST',
            form_params={"action":"vc_get_vc_grid_data","vc_action":"vc_get_vc_grid_data","tag":"vc_basic_grid",
            "data[visible_pages]":"5","data[page_id]":"3056","data[style]":"pagination","data[action]":"vc_get_vc_grid_data",
            "data[shortcode_id]":"1517419843788-afc1f200c7c29bd235e132b0777b3d80-2","data[items_per_page]":"12","data[auto_play]":"false",
            "data[gap]":"30","data[speed]":"-1000","data[loop]":"","data[animation_in]":"","data[animation_out]":"","data[arrows_design]":"vc_arrow-icon-arrow_07_left",
            "data[arrows_color]":"chino","data[arrows_position]":"outside","data[paging_design]":"pagination_rounded","data[paging_color]":"chino",
            "data[tag]":"vc_basic_grid","vc_post_id":"3056","_vcnonce":nonce}
        )


class AppliedTherapeutics(RegexPRScraper):

    URL = 'https://ir.appliedtherapeutics.com'
    NAME = 'Applied Therapeutics'
    SYMBOL = 'APLT'

    async def read_prs(self):
        return await self.read_prs_with_regex(
            r'date-time">\s*([\w, \d\-]+)\s*<\/div>[\s\S]+?<a href="([^"]+)" hreflang="\w+">([^<]+)<\/a>',
            '/news-releases'
        )


class AptorumGroup(RegexPRScraper):

    URL = 'http://ir.aptorumgroup.com'
    NAME = 'Aptorum Group'
    SYMBOL = 'APM'

    async def read_prs(self):
        return await self.read_prs_with_regex(
            r'date-time">\s*([\w, \d\-]+)\s*<\/div>[\s\S]+?<a href="([^"]+)" hreflang="\w+">([^<]+)<\/a>',
            '/news-and-events/press-releases'
        )


class ArcturusTherapeutics(RegexPRScraper):

    URL = 'https://ir.arcturusrx.com'
    NAME = 'Arcturus Therapeutics'
    SYMBOL = 'ARCT'

    async def read_prs(self):
        return await self.read_prs_with_regex(
            r'class="field__item">([\w :,]+)<\/div>[\s\S]+?<a href="([^"]+)" hreflang="\w+">([^<]+)<\/a>',
            '/press-releases'
        )


class AstraZeneca(RegexPRScraper):

    URL = 'https://www.astrazeneca.com'
    NAME = 'AstraZeneca'
    SYMBOL = 'AZN'

    async def read_prs(self):
        return await self.read_prs_with_regex(
            r'<a href="([^"]+?)"[\s\S]+?title">([^<]+?)<[\s\S]+?datetime="([\d\-]+)"',
            '/media-centre/press-releases.html',
            type_to_group={'date': 3, 'url': 1, 'title': 2}
        )


class Capricor(RegexPRScraper):

    URL = 'http://capricor.com'
    NAME = 'Capricor'
    SYMBOL = 'CAPR'

    async def read_prs(self):
        return await self.read_prs_with_regex(
            r'<td>([A-Z][^<]+?)<\/td>\s*<td>\s*<a href="http:\/\/www.irdirect.net([^"]+?)"[ clas="inktrge_b]+?>([^<]+?)<',
            'http://www.irdirect.net/CAPR/press_releases_iframe?per_page=10',
            full_url_path=True, 
            article_url_base='http://www.irdirect.net',
        )


class CELSCI(RegexPRScraper):

    URL = 'https://cel-sci.com'
    NAME = 'CELSCI'
    SYMBOL = 'CVM'

    async def read_prs(self):
        return await self.read_prs_with_regex(
            r'<td>([A-Z][^<]+?)<\/td>\s*<td>\s*<a href="http:\/\/www.irdirect.net([^"]+?)"[ clas="inktrge_b]+?>([^<]+?)<',
            'http://www.irdirect.net/cvm/press_releases_iframe?per_page=10',
            full_url_path=True, 
            article_url_base='http://www.irdirect.net',
        )


class Cidara(RegexPRScraper):

    URL = 'https://ir.cidara.com'
    NAME = 'Cidara'
    SYMBOL = 'CDTX'

    async def read_prs(self):
        return await self.read_prs_with_regex(
            r'class="datetime">([<>="\w /]+?)<\/time>\s*<\/td>[\s\S]*?<a href="([^"]+)" hreflang="\w+">([^<]+)<\/a>',
            '/news-releases'
        )


class Cocrystal(RegexPRScraper):

    URL = 'https://ir.cocrystalpharma.com'
    NAME = 'Cocrystal Pharma'
    SYMBOL = 'COCP'

    async def read_prs(self):
        return await self.read_prs_with_regex(
            r'clearfix">\s*<a href="https:\/\/ir.cocrystalpharma.com([^"]+?)"[\s\S]+?media-heading">([^<]+?)<[\s\S]+?datetime="([\d\-: ]+?)"',
            '/press-releases',
            type_to_group={'date': 3, 'url': 1, 'title': 2}
        )


class Diffusion(GetPressReleaseJSONScraper):

    URL = 'https://investors.diffusionpharma.com'
    NAME = 'Diffusion Pharmaceuticals'
    SYMBOL = 'DFFN'

    async def read_prs(self):
        return await self.read_prs_from_api(
            '/feed/PressRelease.svc/GetPressReleaseList?apiKey=BF185719B0464B3CB809D23926182246' + 
            '&LanguageId=1&bodyType=3&pressReleaseDateFilter=3&categoryId=1cb807d2-208f-4bc3-9133-6a9ad45ac3b0&pageSize=-1' + 
            '&pageNumber=0&tagList=&includeTags=true&year=-1&excludeSelection=1')


class Dynavax(RegexPRScraper):

    URL = 'http://investors.dynavax.com'
    NAME = 'Dynavax'
    SYMBOL = 'DVAX'

    async def read_prs(self):
        return await self.read_prs_with_regex(
            r'<p>([^<]+?)<\/p>[\s\S]+?<a href="([^"]+?)" hreflang="\w+">([^<]+?)<',
            '/press-releases'
        )


class Enanta(GetPressReleaseJSONScraper):

    URL = 'https://www.enanta.com'
    NAME = 'Enanta'
    SYMBOL = 'ENTA'

    async def read_prs(self):
        year = pendulum.now().year
        return await self.read_prs_from_api(
            '/feed/PressRelease.svc/GetPressReleaseList?apiKey=BF185719B0464B3CB809D23926182246' + 
            '&pressReleaseCategoryWorkflowId=1cb807d2-208f-4bc3-9133-6a9ad45ac3b0&bodyType=0' + 
            '&pressReleaseDateFilter=3&pageSize=-1&tagList=&includeTags=true&year={}&excludeSelection=1'.format(year))


class HeatBiologics(RegexPRScraper):

    URL = 'https://www.heatbio.com'
    NAME = 'Heat Biologics'
    SYMBOL = 'HTBX'

    async def read_prs(self):
        return await self.read_prs_with_regex(
            r'media-heading">\s*<a href="([^"]+)">\s*([^<]+)<\/a>\s*<\/h2>\s*<div class="date"><time datetime="([\d\- :]+)"',
            '/news-media/news-releases',
            type_to_group={'date': 3, 'url': 1, 'title': 2}
        )


class Mallinckrodt(RegexPRScraper):

    URL = 'http://www.mallinckrodt.com'
    NAME = 'Mallinckrodt'
    SYMBOL = 'MNK'

    async def read_prs(self):
        return await self.read_prs_with_regex(
            r'<a href="([^"]+?)">([^<]+)<\/a>\s*<span class="news-list-item-date">([^<]+?)<\/',
            '/about/news-and-media/',
            type_to_group={'date': 3, 'url': 1, 'title': 2}
        )


class IMAB(RegexPRScraper):

    URL = 'http://www.i-mabbiopharma.com'
    NAME = 'I-MAB'
    SYMBOL = 'IMAB'

    async def read_prs(self):
        return await self.read_prs_with_regex(
            r'class="date1">\s*([^<]+?)<\/div>\s*?<h3><a href="([^"]+?)">\s*([^<]+?)<\/a',
            '/en/news.aspx',
            article_url_base='http://www.i-mabbiopharma.com/en/'
        )


class JohnsonJohnson(RegexPRScraper):

    URL = 'https://johnsonandjohnson.gcs-web.com'
    NAME = 'Johnson & Johnson'
    SYMBOL = 'JNJ'

    async def read_prs(self):
        return await self.read_prs_with_regex(
            r'date-time"><span class="relSummaryToggle"><\/span>([^<]+?)<[\s\S]+?<a href="([^"]+?)" hreflang="en">([^<]+?)<',
            '/press-releases'
        )


class Kamada(RegexPRScraper):

    URL = 'https://www.kamada.com'
    NAME = 'Kamada'
    SYMBOL = 'KMDA'

    async def read_prs(self):
        return await self.read_prs_with_regex(
            r'"dateDiv">([^<]+?)<\/div>\s*?<div class="newsText">\s*?<h3><a href="https:\/\/www.kamada.com([^"]+)">([^<]+?)<',
            '/news-main/'
        )


class Karyopharm(RegexPRScraper):

    URL = 'https://investors.karyopharm.com'
    NAME = 'Karyopharm Therapeutics'
    SYMBOL = 'KPTI'

    async def read_prs(self):
        return await self.read_prs_with_regex(
            r'class="datetime">([<>="\w, /]+?)<\/time>\s*<\/td>[\s\S]*?<a href="([^"]+)" hreflang="\w+">([^<]+)<\/a>',
            '/press-releases'
        )


class LaJolla(RegexPRScraper):

    URL = 'http://ir.lajollapharmaceutical.com'
    NAME = 'La Jolla Pharmaceutical'
    SYMBOL = 'LJPC'

    async def read_prs(self):
        return await self.read_prs_with_regex(
            r'news--headline">\s*([^<]+?)<\/div>[\s\S]+?date-time">([^<]+?)<[\s\S]+?<a href="([^"]+?)"',
            '/press-releases',
            type_to_group={'date': 2, 'url': 3, 'title': 1}
        )


class Ligand(RegexPRScraper):

    URL = 'https://investor.ligand.com'
    NAME = 'Ligand Pharmaceuticals'
    SYMBOL = 'LGND'

    async def read_prs(self):
        return await self.read_prs_with_regex(
            r'media">\s*<a href="https:\/\/investor.ligand.com([^"]+)">[\s\S]+?media-heading">([^<]+?)<\/h2>\s*?<p class="date"><time datetime="([\d:\- ]+)"',
            '/press-releases',
            type_to_group={'date': 3, 'url': 1, 'title': 2}
        )


class VirBio(RegexPRScraper):

    URL = 'https://investors.vir.bio'
    NAME = 'Vir Biotechnology'
    SYMBOL = 'VIR'

    async def read_prs(self):
        return await self.read_prs_with_regex(
            r'date-time">([^<]+?)<[\s\S]+?<a href="([^"]+?)" hreflang="en">([^<]+?)<\/a>',
            '/press-releases'
        )


class VBIVacc(RegexPRScraper):

    URL = 'https://www.vbivaccines.com'
    NAME = 'VBI Vaccines'
    SYMBOL = 'VBIV'

    async def read_prs(self):
        return await self.read_prs_with_regex(
            r'<a href="https:\/\/www.vbivaccines.com([^"]+?)"[\s\S]+?mark">([^<]+)<[\s\S]+?datetime="([\d\-T:]+)"',
            '/wire/'
        )


class Vaxart(RegexPRScraper):

    URL = 'https://investors.vaxart.com'
    NAME = 'Vaxart'
    SYMBOL = 'VXRT'

    async def read_prs(self):
        return await self.read_prs_with_regex(
            r'date-wrap">\s*([^<]+)<\/td>\s*?<td>\s*<a href="([^"]+?)" class="[\w\-]+">\s*?([^<]+?)<',
            '/press-releases'
        )


class Sanofi(RegexPRScraper):

    URL = 'https://www.sanofi.com'
    NAME = 'Sanofi'
    SYMBOL = 'SNY'

    async def read_prs(self):
        return await self.read_prs_with_regex(
            r'<a title="([^"]+)" href="([^"]+)">[\s\S]+?osw-js-date">([^<]+?)<',
            '/en/media-room/press-releases',
            type_to_group={'date': 3, 'url': 2, 'title': 1}
        )


class Vanda(RegexPRScraper):

    URL = 'https://www.vandapharma.com'
    NAME = 'Vanda Pharmaceuticals'
    SYMBOL = 'VNDA'

    async def read_prs(self):
        return await self.read_prs_with_regex(
            r'<h6>([^<]+?)<\/h6>\s*<a href="([^"]+?)" target="_blank"><p>\s*?([^<]+?)<',
            '/investors',
            article_url_base=""
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
    Moleculin,
    SCWORX,
    Agenus,
    ImmunoTech,
    Aldeyra,
    Altimmune,
    Amgen,
    AppliedDNASciences,
    AppliedTherapeutics,
    AptorumGroup,
    AstraZeneca,
    Capricor,
    CELSCI,
    Cidara,
    Cocrystal,
    Diffusion,
    Dynavax,
    Enanta,
    HeatBiologics,
    IMAB,
    JohnsonJohnson,
    Kamada,
    Karyopharm,
    LaJolla,
    Ligand,
    VirBio,
    Vaxart,
    Sanofi,
    Vanda
]