import yaml
import os


PROJECT_DIR = os.path.join(os.path.dirname(__file__), '..')


config = yaml.safe_load(open(os.path.join(PROJECT_DIR, 'config.yaml')))

try:
    config['creds'] = yaml.safe_load(open(os.path.join(PROJECT_DIR, 'creds.yaml')))
except:
    raise Exception('creds.yaml not found!')

try:
    config['symbols'] = yaml.safe_load(open(os.path.join(PROJECT_DIR, 'symbols.yaml')))
    config['symbols_list_all'] = list(config['symbols'].keys())
except:
    raise Exception('symbols.yaml not found!')