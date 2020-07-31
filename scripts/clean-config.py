from finnews.config import config
import yaml
import os


def _clean_recur(data):
    for key, item in data.items():
        if type(item) == dict:
            _clean_recur(item)
        elif type(item) == list:
            list_sorted = sorted(set(item))
            data[key] = list_sorted


def clean(fn):
    with open(fn, "r") as f:
        cfg = yaml.safe_load(f)
    _clean_recur(cfg)
    with open(fn, "w") as f:
        yaml.safe_dump(cfg, f)


if __name__ == "__main__":
    clean(config["config_fn"])
    clean(config["symbols_fn"])

