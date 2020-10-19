from collections import defaultdict
from finnews.utils import config, run_many
import glob
import os


def merge_prices():

    print("Finding tick csv files to merge...", end="")
    fns_by_symbol = defaultdict(list)
    for fn in glob.iglob(os.path.join(config["data_dir"], "watch", "ticks", "P_*.csv")):
        fn_split = fn[:-4].split("_")
        sym = fn_split[-2]
        fns_by_symbol[sym].append(fn)
    print("done")

    run_many(_do_price_merge, list(fns_by_symbol.items()), tdqm=True)


def _do_price_merge(params):
    sym, fns = params
    if len(fns) <= 1:
        return
    fns = sorted(fns)
    header = None
    content_by_date = {}
    for fn in fns:
        with open(fn, "r") as f:
            for i, line in enumerate(f.readlines()):
                line = line.strip()
                if len(line) == 0:
                    continue
                if i == 0:
                    if header is not None:
                        if header != line:
                            print("[{}] Expected {} to be {}".format(sym, line, header))
                            return
                    else:
                        header = line
                else:
                    splt = line.split(",")
                    date = splt[0]
                    data = ",".join(splt[1:])
                    content_by_date[date] = data
    with open(fns[0], "w") as f:
        f.write(header + "\n")
        for dt in sorted(content_by_date):
            val = content_by_date[dt]
            f.write(dt + "," + val + "\n")
    for mfn in fns[1:]:
        os.remove(mfn)


def main():
    merge_prices()


if __name__ == "__main__":
    main()
