from collections import defaultdict
from finnews.utils import config, run_many, ensure_dirs
import pylru
import tqdm
import json
import glob
import os


def reindex_all():
    events_fns = sorted(glob.glob(os.path.join(config["data_dir"], "watch", "date", "*")))
    temp_sym_dir = os.path.join(config["data_dir"], "watch", "syms-temp")
    if os.path.exists(temp_sym_dir):
        raise Exception(temp_sym_dir + " exists!")
    ensure_dirs([temp_sym_dir])
    cache = pylru.lrucache(2048)
    dup_cnt = 0
    too_many_cnt = 0
    corrupt_cnt = 0
    syms_seen = set()
    for fn in tqdm.tqdm(events_fns):
        with open(fn, "r") as f:
            for line in f.readlines():
                if len(line) == 0:
                    continue
                try:
                    evt = json.loads(line.strip())
                except Exception as e:
                    corrupt_cnt += 1
                evt_type = evt.get("type", "unk")
                evt_symbols = evt.get("symbols", [])
                if evt_type == "error":
                    continue
                if len(evt_symbols) is None:
                    syms = ["_NONE"]
                else:
                    syms = [s for s in evt_symbols if s not in [".", "..."]]
                if len(syms) > 5:
                    # discard events that have too many labels
                    too_many_cnt += 1
                    continue
                cache_key = (
                    ",".join(syms)
                    + evt_type
                    + evt.get("source", "")
                    + evt.get("title", "")
                    + evt.get("text", "")[:100]
                    + evt.get("name", "")
                    + str(evt.get("value", ""))
                )
                if cache_key in cache:
                    dup_cnt += 1
                    continue
                cache[cache_key] = evt
                for sym in syms:
                    syms_seen.add(sym)
                    try:
                        with open(os.path.join(temp_sym_dir, sym), "a") as f2:
                            f2.write(line)
                    except Exception as e:
                        print(e)
    print("Duplicates", dup_cnt)
    print("Corruptions", corrupt_cnt)
    print("Too many labels", too_many_cnt)
    print("Unique Symbols", len(syms_seen))


if __name__ == "__main__":
    reindex_all()
