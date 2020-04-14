import yaml
import os


PROJECT_DIR = os.path.join(os.path.dirname(__file__), '..')
CONFIG_FN = os.path.join(PROJECT_DIR, 'config.yaml')


def _clean_recur(data):
    for key, item in data.items():
        if type(item) == dict:
            _clean_recur(item)
        elif type(item) == list:
            list_sorted = sorted(set(item))
            data[key] = list_sorted


def main():
    with open(CONFIG_FN, 'r') as f:
        config = yaml.safe_load(f)
    _clean_recur(config)
    with open(CONFIG_FN, 'w') as f:
        config = yaml.safe_dump(config, f)


if __name__ == '__main__':
    main()