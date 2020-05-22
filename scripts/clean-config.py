import yaml
import os


PROJECT_DIR = os.path.join(os.path.dirname(__file__), '..')


def _clean_recur(data):
    for key, item in data.items():
        if type(item) == dict:
            _clean_recur(item)
        elif type(item) == list:
            list_sorted = sorted(set(item))
            data[key] = list_sorted


def clean(fn):
    with open(fn, 'r') as f:
        config = yaml.safe_load(f)
    _clean_recur(config)
    with open(fn, 'w') as f:
        yaml.safe_dump(config, f)


if __name__ == '__main__':
    clean(os.path.join(PROJECT_DIR, 'config.yaml'))
    clean(os.path.join(PROJECT_DIR, 'symbols.yaml'))