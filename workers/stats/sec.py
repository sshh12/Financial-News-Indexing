from . import MetaDataSource
from articles import clean_html_text
from bs4 import BeautifulSoup
import pendulum
import re


class SEC(MetaDataSource):
    def __init__(self):
        self.url = "https://www.sec.gov"

    async def read_latest_filings(self):
        resp = await self._get(
            "/cgi-bin/browse-edgar?action=getcurrent&CIK=&type=&company=&dateb=&owner=include&start=0&count=40&output=atom"
        )
        bs = BeautifulSoup(resp, "lxml")
        filings = []
        for entry in bs.feed.findAll("entry"):
            title = entry.title.text
            link = entry.link["href"]
            filings.append((title, link))
        return "sec", filings

    async def resolve_filing(self, url):
        txt_url = url.replace("-index.htm", ".txt").replace(self.url, "")
        raw = await self._get(txt_url)

        data = {}

        parser = SECFileParser(txt_url, raw)
        parser.parse_header()
        if parser.form not in ["10-Q", "10-Q/A"]:
            print(parser.form)
            return None
        if parser.comp_id is None:
            return None
        parser.parse_text()

        data["company"] = parser.headers.get("company_data_company_conformed_name", "")
        data["company_class"] = parser.headers.get("company_data_standard_industrial_classification", "")
        data["name"] = parser.form
        # data['text'] = parser.text
        print(parser.text)

        return data


class SECFileParser:
    def __init__(self, url, text):
        self.url = url
        self.raw = text

        self.headers = {}
        self.form = None
        self.comp_id = None
        self.text = ""

    def parse_header(self):
        group = ""
        header_txt = self.raw[: self.raw.index("</SEC-HEADER>")]
        for match in re.finditer(r"\t+?([A-Z\d ]+?):\t*([^\n]*?)\n", header_txt):
            key = match.group(1).strip().replace(" ", "_").lower()
            val = match.group(2).strip()
            if len(val) == 0:
                group = key
            else:
                self.headers[group + "_" + key] = val
        self.form = self.headers.get("filing_values_form_type")
        self.comp_id = self.headers.get("company_data_central_index_key")

    def parse_text(self):
        start_idx = self.raw.index("<DOCUMENT>\n<TYPE>" + self.form)
        end_idx = self.raw.index("</DOCUMENT>", start_idx)
        body = self.raw[start_idx:end_idx]
        delete_tokens = ["&nbsp;"]
        delete_tags = [
            "XBRL" "div",
            "font",
            "FONT",
            "p",
            "body",
            "P",
            "U",
            "B",
            "DIV",
            "HTML",
            "TEXT",
            "I",
            "span",
            "SPAN",
            "a",
            "ix:nonNumeric",
            "html",
            "ix:nonFraction",
            "ix:continuation",
        ]
        repl_regex = [
            ("<\/?hr[^>]*?>", "\n\n"),
            ("<\/?br[^>]*?>", "\n\n"),
            ("<!--[\s\S]+?-->", ""),
            ("<A[\s\S]+?<\/A>", ""),
            ("<head[\s\S]+?<\/head>", ""),
            ("<TABLE[\s\S]+?<\/TABLE>", ""),
            ("<table[\s\S]+?<\/table>", ""),
            ("<ix:header[\s\S]+?<\/ix:header>", ""),
            ("\\| \\d+\n", "\n\n"),
            ("([\w\.])\n([&\w])", r"\1 \2"),
            ("([a-z])([A-Z])", r"\1 \2"),
            ("\n\s+\n", "\n\n"),
            ("\n{3,}", "\n\n"),
        ]
        for token in delete_tokens:
            body = body.replace(token, "")
        for tag in delete_tags:
            reg = "<\/?" + tag + "[^>]*?>"
            body = re.sub(reg, "", body)
        for pat, repl in repl_regex:
            body = re.sub(pat, repl, body)
        body = clean_html_text(body)
        self.text = body
