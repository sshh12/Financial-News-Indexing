from finnews.articles.seekingalpha import SeekingAlpha
from finnews.articles.marketwatch import MarketWatch
from finnews.articles.reuters import Reuters
from finnews.articles.prnewswire import PRNewsWire
from finnews.articles.rttnews import RTTNews
from finnews.articles.moodys import Moodys
from finnews.articles.businesswire import BusinessWire
from finnews.articles.federalreserve import FederalReserve
from finnews.articles.globenewswire import GlobeNewsWire
from finnews.articles.accesswire import AccessWire
from finnews.articles.stocktwits import StockTwits
from finnews.articles.businessinsider import BusinessInsider
from finnews.articles.marketexclusive import MarketExclusive
from finnews.articles.alphastocknews import AlphaStockNews
from finnews.articles.usbls import USBLS
from finnews.articles.stat import STAT
from finnews.articles.fitch import Fitch
from finnews.articles.thestreet import TheStreet
from finnews.articles.cnn import CNN
from finnews.articles.barrons import Barrons
from finnews.articles.forbes import Forbes
from finnews.articles.benzinga import Benzinga
from finnews.articles.pharmiweb import PharmiWeb
from finnews.articles.financialtimes import FinancialTimes
from finnews.articles.streetinsider import StreetInsider
from finnews.articles.miningnewsfeed import MiningNewsFeed
from finnews.articles.yahoo import Yahoo


ARTICLE_SOURCES = {
    "prnewswire": PRNewsWire,
    "reuters": Reuters,
    "marketwatch": MarketWatch,
    "seekingalpha": SeekingAlpha,
    "rtt": RTTNews,
    "moodys": Moodys,
    "businesswire": BusinessWire,
    "federalreserve": FederalReserve,
    "usbls": USBLS,
    "globenewswire": GlobeNewsWire,
    "accesswire": AccessWire,
    "stocktwits": StockTwits,
    "stat": STAT,
    "fitch": Fitch,
    "thestreet": TheStreet,
    "barrons": Barrons,
    "cnn": CNN,
    "businessinsider": BusinessInsider,
    "forbes": Forbes,
    "marketexclusive": MarketExclusive,
    "alphastocknews": AlphaStockNews,
    "benzinga": Benzinga,
    "pharmiweb": PharmiWeb,
    "financialtimes": FinancialTimes,
    "streetinsider": StreetInsider,
    "miningnewsfeed": MiningNewsFeed,
    "yahoo": Yahoo,
}
