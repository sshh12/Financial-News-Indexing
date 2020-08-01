from finnews.stats.finviz import FinViz
from finnews.stats.zacks import Zacks
from finnews.stats.earningscast import EarningsCast
from finnews.stats.biopharmcatalyst import BioPharmCatalyst


STAT_SOURCES = {"finviz": FinViz, "zacks": Zacks, "earningscast": EarningsCast, "biopharmcatalyst": BioPharmCatalyst}
