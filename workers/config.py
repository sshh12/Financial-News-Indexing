import yaml
import os


PROJECT_DIR = os.path.join(os.path.dirname(__file__))


config = yaml.safe_load(open(os.path.join(PROJECT_DIR, 'workers.yaml')))