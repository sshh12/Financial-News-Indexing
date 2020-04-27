from pymeritrade import TDAClient
from config import config
from . import Stream


CREDS = config['creds']['tda']


class StreamTDA(Stream):

    def __init__(self):
        pass

    def start(self):
        pass