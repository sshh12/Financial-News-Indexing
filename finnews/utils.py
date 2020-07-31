from finnews.config import config
from multiprocessing import Pool
import tqdm
import os


def ensure_dirs(paths):
    if isinstance(paths, str):
        paths = [paths]
    for path in paths:
        os.makedirs(path, exist_ok=True)


def run_many(f, args, mode="multiprocessing", starmap=False, workers=None, tdqm=False):
    assert mode == "multiprocessing"
    with Pool(processes=workers) as pool:
        if starmap:
            map_func = pool.starmap
        else:
            map_func = pool.imap_unordered
        if tqdm:
            map_func_log = lambda func, func_args: tqdm.tqdm(map_func(func, func_args), total=len(func_args))
        else:
            map_func_log = map_func
        for _ in map_func_log(f, args):
            pass
