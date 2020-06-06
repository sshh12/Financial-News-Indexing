from articles.seekingalpha import SeekingAlpha
from articles.marketwatch import MarketWatch
from articles.reuters import Reuters
from articles.prnewswire import PRNewsWire
from articles.rttnews import RTTNews
from articles.moodys import Moodys
from articles.businesswire import BusinessWire
from articles.federalreserve import FederalReserve
from articles.globenewswire import GlobeNewsWire
from articles.accesswire import AccessWire
from articles.stocktwits import StockTwits
from articles.businessinsider import BusinessInsider
from articles.marketexclusive import MarketExclusive
from articles.alphastocknews import AlphaStockNews
from articles.usbls import USBLS
from articles.stat import STAT
from articles.fitch import Fitch
from articles.thestreet import TheStreet
from articles.cnn import CNN
from articles.barrons import Barrons
from articles.forbes import Forbes
from articles.benzinga import Benzinga
from articles.pharmiweb import PharmiWeb
from articles.financialtimes import FinancialTimes
from articles.streetinsider import StreetInsider
from articles.miningnewsfeed import MiningNewsFeed
from articles.yahoo import Yahoo


STREAM_SOURCES = {
    'prnewswire': PRNewsWire,
    'reuters': Reuters,
    'marketwatch': MarketWatch,
    'seekingalpha': SeekingAlpha,
    'rtt': RTTNews,
    'moodys': Moodys,
    'businesswire': BusinessWire,
    'federalreserve': FederalReserve,
    'usbls': USBLS,
    'globenewswire': GlobeNewsWire,
    'accesswire': AccessWire,
    'stocktwits': StockTwits,
    'stat': STAT,
    'fitch': Fitch,
    'thestreet': TheStreet,
    'barrons': Barrons,
    'cnn': CNN,
    'businessinsider': BusinessInsider,
    'forbes': Forbes,
    'marketexclusive': MarketExclusive,
    'alphastocknews': AlphaStockNews,
    'benzinga': Benzinga,
    'pharmiweb': PharmiWeb,
    'financialtimes': FinancialTimes,
    'streetinsider': StreetInsider,
    'miningnewsfeed': MiningNewsFeed,
    'yahoo': Yahoo
}
