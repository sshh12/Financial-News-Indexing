from collections import defaultdict
import pandas as pd
import tqdm
import glob
import os


def merge_prices():

    fns_by_symbol = defaultdict(list)
    for fn in glob.iglob(os.path.join('data', 'watch', 'ticks', 'P_*.csv')):
        fn_split = fn[:-4].split('_')
        sym = fn_split[1]
        fns_by_symbol[sym].append(fn)

    for sym, fns in tqdm.tqdm(fns_by_symbol.items()):
        if len(fns) <= 1:
            continue
        fns = sorted(fns)
        df_base = pd.read_csv(fns[0], index_col=0, parse_dates=True)
        for mfn in fns[1:]:
            df_other = pd.read_csv(mfn, index_col=0, parse_dates=True)
            df_base = pd.concat([df_base, df_other], axis=0)
            df_base = df_base.loc[~df_base.index.duplicated(keep='first')]
        df_base = df_base.sort_index()
        df_base.to_csv(fns[0])
        for mfn in fns[1:]:
            os.remove(mfn)


def merge_options():
    
    fns_by_symbol = defaultdict(list)
    for fn in glob.iglob(os.path.join('data', 'watch', 'ticks', 'O_*.csv')):
        fn_split = fn[:-4].split('_')
        sym = fn_split[1]
        ts = fn_split[2]
        fns_by_symbol[sym].append((fn, ts))

    for sym, fns in tqdm.tqdm(fns_by_symbol.items()):
        if len(fns) <= 1:
            continue
        fns = sorted(fns)
        base_fn, base_ts = fns[0]
        df_base = pd.read_csv(base_fn)
        if 'option_idx' not in df_base.columns:
            df_base['option_idx'] = base_ts + '_' + df_base['option_symbol']
        for mfn, mts in fns[1:]:
            df_other = pd.read_csv(mfn)
            df_other['option_idx'] = mts + '_' + df_other['option_symbol']
            df_base = pd.concat([df_base, df_other], ignore_index=True, axis=0, sort=False)
        df_base = df_base.set_index('option_idx').sort_index()
        df_base.to_csv(base_fn)
        for mfn, _ in fns[1:]:
            os.remove(mfn)


def main():
    merge_prices()
    merge_options()


if __name__ == '__main__':
    main()