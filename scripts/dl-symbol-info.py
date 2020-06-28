import requests
import tqdm
import yaml
import re
import os


PROJECT_DIR = os.path.join(os.path.dirname(__file__), "..")


def mw_tags(sym):
    try:
        resp = requests.get("https://www.marketwatch.com/investing/stock/{}/profile".format(sym)).text
        name = re.search(r'companyinfo fourwide">\s*<p class="companyname">([^<]+?)<', resp).group(1).strip()
        industry = re.search(r'Industry<\/p>\s*<p class="data lastcolumn">([^<]+?)<\/p>', resp).group(1).strip()
        sector = re.search(r'Sector<\/p>\s*<p class="data lastcolumn">([^<]+?)<\/p>', resp).group(1).strip()
        return dict(name=name, industry=industry, sector=sector)
    except:
        return None


def sec_cik(sym):
    try:
        resp = requests.get(
            "https://www.sec.gov/cgi-bin/browse-edgar?CIK={}&owner=exclude&action=getcompany".format(sym)
        ).text
        cik = re.search(r'name="CIK" value="(\d+)"', resp).group(1).strip()
        return cik
    except:
        return None


FIELDS = {"mw_tags": mw_tags, "sec_cik": sec_cik}


def main():

    sym_fn = os.path.join(PROJECT_DIR, "symbols.yaml")

    with open(sym_fn, "r") as f:
        symbols = yaml.safe_load(f)

    for sym in tqdm.tqdm(symbols):
        for field, func in FIELDS.items():
            if field not in symbols[sym]:
                val = func(sym)
                if val is not None:
                    symbols[sym][field] = val

    with open(sym_fn, "w") as f:
        yaml.safe_dump(symbols, f)


if __name__ == "__main__":
    main()
