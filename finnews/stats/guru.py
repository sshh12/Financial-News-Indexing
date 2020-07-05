from . import MetaDataSource
import subprocess
import pendulum
import tempfile
import json
import os
import re


def _exec_js(code):
    with tempfile.TemporaryDirectory() as tmp_dir:
        js_path = os.path.join(tmp_dir, "tmp.js")
        with open(js_path, "w") as f:
            f.write(code)
        result = subprocess.run(["node", js_path], stdout=subprocess.PIPE)
        out = str(result.stdout, "utf-8")
        return json.loads(out)


def _flatten_guru(d, parent_key="", sep="_"):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        new_key = new_key.replace(" ", "_").replace("meidum", "medium").lower()
        if isinstance(v, dict):
            items.extend(_flatten_guru(v, new_key, sep=sep).items())
        elif isinstance(v, list) or (
            "display_name" in k
            or "origin_key" in k
            or "_timestamp" in k
            or k.endswith("_display")
            or k.endswith("_name")
        ):
            pass
        else:
            items.append((new_key, v))
    return dict(items)


class Guru(MetaDataSource):
    def __init__(self):
        self.url = "https://www.gurufocus.com"

    async def read_financials(self, sym):
        resp = await self._get("/stock/{}/summary".format(sym))
        js_script = re.search(r"window.__NUXT__=([\s\S]+?);<\/script>", resp).group(1)
        try:
            raw_data = _exec_js("console.log(JSON.stringify(" + js_script + ".data[0].stock))")
            raw_data.update(_exec_js("console.log(JSON.stringify(" + js_script + ".data[1].summaryView.data))"))
        except json.decoder.JSONDecodeError:
            return "guru", None, None
        else:
            data = _flatten_guru(raw_data)
            assert data["symbol"] == sym
            if "timestamp" in data:
                del data["timestamp"]
            return "guru", sym, data

