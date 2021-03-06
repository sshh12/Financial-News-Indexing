from finnews.utils import config
import newspaper
import pendulum
import re


def clean_html_text(html):
    html_codes = [
        ("&rsquo;", "'"),
        ("&lsquo;", "'"),
        ("&ldquo;", '"'),
        ("&rdquo;", '"'),
        ("&quot;", '"'),
        ("&amp;", "&"),
        ("&ntilde;", "n"),
        ("&copy;", ""),
        ("&#8217;", "'"),
        ("&#160;", " "),
        ("&nbsp;", " "),
        ("&otilde;", "o"),
        ("&ccedil;", "c"),
        ("&lt;", "<"),
        ("&gt;", ">"),
        ("&ndash;", "-"),
        ("&mdash;", "-"),
        ("&uuml;", "u"),
        ("&oacute;", "o"),
        ("&mu;", "μ"),
        ("&eacute;", "e"),
        ("&ouml;", "o"),
        ("&reg;", ""),
        ("&auml;", "a"),
        ("&iacute;", "i"),
        ("&uacute;", "u"),
        ("&raquo;", '"'),
        ("&laquo;", '"'),
        ("&ocirc;", "o"),
        ("&agrave;", "a"),
        ("&Eacute;", "E"),
        ("&ucirc;", "u"),
        ("&Agrave;", "A"),
        ("&egrave;", "e"),
        ("&ugrave;", "u"),
        ("&aacute;", "a"),
        ("&ocirc;", "o"),
        ("&trade;", ""),
    ]
    weird_tokens = [
        ("•", "*"),
        ("●", "* "),
        ("\u2019", "'"),
        ("\r", ""),
        ("…", "..."),
        ("—", "-"),
        ("ー", "-"),
        ("‘", "'"),
        ("’", "'"),
        ("“", ""),
        ("”", ""),
        ("»", '"'),
        ("«", '"'),
        ("™", ""),
        ("\u200d", ""),
        ("\u2013", "-"),
        ("Â\xa0", " "),
        ("Â½", ""),
        ("®", ""),
        ("\xa0", " "),
        ("✅", ""),
        ("→", "->"),
        ("💯", ""),
        ("🚨", ""),
    ]
    for bad_token, repl in html_codes + weird_tokens:
        html = html.replace(bad_token, repl)
    html = re.sub(r'<style[\s\w=":/\.\-,\'!%&+@\|{}\(\);#~\?]*>([\s\S]+?)<\/style>', "", html)
    html = re.sub(r'<script[\s\w=":/\.\-,\'!%&+@\|{}\(\);#~\?]*>([\s\S]+?)<\/script>', "", html)
    html = re.sub(r'<\w+[\s\w=":/\.\-,\'!%&+@\|#~{}\(\);\?]*>', "", html)
    html = re.sub(r"<\/?[\w\-]+>", "", html)
    html = re.sub(r"<!-*[^>]+>", "", html)
    html = re.sub(r"&#[\w\d]+;", "", html)
    html = re.sub(r"\s{3,}", " ", html)
    html = re.sub(r"https:\/\/t.co\/[\w]+", " ", html)
    html = re.sub(r"RT @\w+:", "", html)
    html = re.sub("([a-z])\s{2,}([A-Z])", "\\1 \\2", html)
    html = html.replace(" (Updated)", "")
    return html.strip()


def url_to_n3karticle(url, input_html=None):
    art = newspaper.Article(url)
    art.download(input_html=input_html)
    art.parse()
    return art


def _timezone_to_offset(date_string):
    return date_string.replace("ET", "-0500").replace("EST", "-0500").replace("EDT", "-0400").replace("UTC", "-0000")


def text_to_datetime(html):

    ## https://pendulum.eustace.io/docs/

    text = clean_html_text(html)

    # 2019-04-12T18:12:00Z
    # 2019-06-26T20:20:19.280Z
    # 2019-06-28T20:22:22+00:00
    try:
        return pendulum.parse(text).in_tz(config["tz"])
    except ValueError:
        pass

    # 2019-07-05T11:32-500
    try:
        parts = text.split("-")
        parts[-1] = "0" + parts[-1]
        return pendulum.parse("-".join(parts)).in_tz(config["tz"])
    except (ValueError, IndexError):
        pass

    # June 27, 2019 6:51pm
    # June 18, 2019 10:40am
    try:
        time_text = text.replace("am", "AM").replace("pm", "PM")
        return pendulum.from_format(time_text, "MMMM D, YYYY h:mmA").in_tz(config["tz"])
    except (ValueError, IndexError):
        pass

    # JUNE 26, 2019 3:01 PM
    try:
        time_text = text.replace("am", "AM").replace("pm", "PM")
        return pendulum.from_format(time_text, "MMMM D, YYYY h:mm A").in_tz(config["tz"])
    except (ValueError, IndexError):
        pass

    # June 27, 2019 11:47 am ET
    # June 26, 2019 4:07 p.m. ET
    # March 24, 2020 at 9:11 a.m. ET
    try:
        time_text = _timezone_to_offset(
            text.replace(" at ", " ").replace(".", "").replace(",", "").replace("am", "AM").replace("pm", "PM")
        )
        return pendulum.from_format(time_text, "MMMM D YYYY h:mm A ZZ").in_tz(config["tz"])
    except (ValueError, IndexError):
        pass

    # Jul 5, 2019 12:30 UTC
    try:
        time_text = _timezone_to_offset(text.replace(".", "").replace(",", ""))
        return pendulum.from_format(time_text, "MMM D YYYY H:mm ZZ").in_tz("UTC")
    except (ValueError, IndexError):
        pass

    # Jul 25 2018 6:09 PM EDT
    try:
        time_text = _timezone_to_offset(text.replace(".", "").replace(",", "").replace("am", "AM").replace("pm", "PM"))
        return pendulum.from_format(time_text, "MMM D YYYY h:mm A ZZ").in_tz("UTC")
    except (ValueError, IndexError):
        pass

    # 4 hours ago
    try:
        hours_ago = int(re.search(r"(\d) hours?", text).group(1))
        return pendulum.now().subtract(hours=hours_ago).in_tz("UTC")
    except AttributeError:
        pass

    # Mon Mar 23 16:05:53 +0000 2020
    try:
        return pendulum.from_format(time_text, "ddd MMM D HH:mm:ss ZZ YYYY").in_tz(config["tz"])
    except (ValueError, AttributeError):
        pass

    # April 02, 2020
    try:
        time_text = text.replace(",", "")
        return pendulum.from_format(time_text, "MMMM DD YYYY").in_tz(config["tz"])
    except (ValueError, AttributeError):
        pass

    # 31 March 2020
    try:
        time_text = text.replace(",", "")
        return pendulum.from_format(time_text, "DD MMMM YYYY").in_tz(config["tz"])
    except (ValueError, AttributeError):
        pass

    # 11 Mar. 2020
    try:
        time_text = text.replace(",", "").replace(".", "")
        return pendulum.from_format(time_text, "DD MMM YYYY").in_tz(config["tz"])
    except (ValueError, AttributeError):
        pass

    # Apr 7, 2020
    try:
        time_text = text.replace(",", "")
        return pendulum.from_format(time_text, "MMM D YYYY").in_tz(config["tz"])
    except (ValueError, AttributeError):
        pass

    # Apr022020
    # Mar 10, 2020
    try:
        time_text = text.replace(",", "").replace(" ", "")
        return pendulum.from_format(time_text, "MMMDDYYYY").in_tz(config["tz"])
    except (ValueError, AttributeError):
        pass

    # 03/31/20
    # 03.27 2020
    # 03 27 2020
    try:
        time_text = text.replace(".", " ").replace("/", "-").replace(" ", "-")
        return pendulum.from_format(time_text, "MM-DD-YY").in_tz(config["tz"])
    except (ValueError, AttributeError):
        pass

    raise ValueError("Not a valid datetime string" + text)


def string_contains(text, items):
    text = text.lower()
    for item in items:
        item_lower = item.lower()
        if item_lower in text:
            return True
    return False


def truncate_sentence(text):
    text_fix = text.replace("U.S.", "U_S_")

    def first_index(token):
        try:
            return text_fix.index(token, 5)
        except:
            return len(text)

    idx = min([first_index("."), first_index("?"), first_index("!"), first_index("\n")])
    return text[: idx + 1]


def tokenize(text):
    text = re.sub(r"[!\.\?\n\r,]", "", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.split(" ")


def extract_symbols(text, strict=False, _token_to_sym={}):
    symbs = set()

    plain_text = re.sub(r"[!,#\.\?\n\r]", "", text).replace("'s ", " ")
    if len(_token_to_sym) == 0:
        for sym, sym_data in config["symbols"].items():
            for kw in sym_data.get("kws", []):
                _token_to_sym[kw] = sym
    for token, sym in _token_to_sym.items():
        try:
            idx = plain_text.index(token)
            end_idx = idx + len(token)
        except ValueError:
            continue
        if (idx == 0 or plain_text[idx - 1] == " ") and (end_idx == len(plain_text) or plain_text[end_idx] == " "):
            symbs.add(sym)

    ticker_regexs = [
        r"NASDAQ:\s?([A-Z\.]+)\b",
        r"NASD:\s?([A-Z\.]+)\b",
        r"Nasdaq:\s?([A-Z\.]+)\b",
        r"ticker:\s*([A-Z\.]+?)\b",
        r"NYSE\/?[A-Z]*?:\s?([A-Z\.]+)\b",
    ]

    for ticker_rgx in ticker_regexs:
        for match in re.finditer(ticker_rgx, text):
            symbs.add(match.group(1))

    if not strict:
        for match in re.finditer(r"\$([A-Z\.]+)\b", text):
            symbs.add(match.group(1))
        for match in re.finditer(r" \(([A-Z\.]+)\)", text):
            symbs.add(match.group(1))

    return symbs
