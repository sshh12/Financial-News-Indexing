import yaml
import os


PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CONFIG_FN = os.environ.get("FINNEWS_CONFIG", os.path.join(PROJECT_DIR, "config.yaml"))
CONFIG_DIR = os.path.dirname(CONFIG_FN)

with open(CONFIG_FN, "r") as cf:
    config = yaml.safe_load(cf)
config["config_fn"] = CONFIG_FN
config.setdefault("creds_fn", os.path.join(CONFIG_DIR, "creds.yaml"))
config.setdefault("symbols_fn", os.path.join(CONFIG_DIR, "symbols.yaml"))
config.setdefault("data_dir", os.path.join(CONFIG_DIR, "data"))
config.setdefault("tz", "UTC")

try:
    with open(config["creds_fn"], "r") as cf:
        config["creds"] = yaml.safe_load(cf)
except:
    raise Exception("creds.yaml not found!")

try:
    with open(config["symbols_fn"], "r") as cf:
        config["symbols"] = yaml.safe_load(cf)
    config["symbols_list_all"] = list(config["symbols"].keys())
except:
    raise Exception("symbols.yaml not found!")

