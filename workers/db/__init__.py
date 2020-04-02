from playhouse.postgres_ext import PostgresqlExtDatabase
from peewee import *

from config import config


POSTGRES_CREDS = config['creds']['postgres']
db = PostgresqlExtDatabase(
    POSTGRES_CREDS['name'], 
    user=POSTGRES_CREDS['user'], 
    password=POSTGRES_CREDS['password'], 
    host=POSTGRES_CREDS['host']
)


class Symbol(Model):

    symbol = CharField(unique=True, primary_key=True)
    name = CharField(unique=True)
    desc = TextField(null=True)
    industry = CharField(null=True)
    sector = CharField(null=True)
    asset_type = CharField()

    class Meta:
        database = db


class Article(Model):

    article_id = CharField(unique=True, primary_key=True) 
    title = CharField()
    content = TextField(null=True)
    url = CharField()
    source = CharField()
    published = DateTimeField()
    found = DateTimeField()

    class Meta:
        database = db


class SymbolArticle(Model):

    symbol = ForeignKeyField(Symbol)
    article = ForeignKeyField(Article)

    class Meta:
        primary_key = CompositeKey('symbol', 'article')
        database = db


class OHLCV(Model):
    
    symbol = ForeignKeyField(Symbol, backref='ohlcvs', null=True)
    open = DoubleField(null=True)
    high = DoubleField(null=True)
    low = DoubleField(null=True)
    close = DoubleField(null=True)
    volume = DoubleField(null=True)
    source = CharField()
    start = DateTimeField()
    end = DateTimeField()
    period = IntegerField()

    class Meta:
        database = db


class Stat(Model):
    
    symbol = ForeignKeyField(Symbol, backref='stats', null=True)
    category = CharField()
    name = CharField()
    source = CharField()
    value = DoubleField()
    published = DateTimeField()
    found = DateTimeField()
    effect = DateTimeField()
    period = IntegerField()

    class Meta:
        database = db


MODELS = [Symbol, Article, SymbolArticle, OHLCV, Stat]
# db.drop_tables(MODELS)
# db.create_tables(MODELS)