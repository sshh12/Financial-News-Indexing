from playhouse.postgres_ext import PostgresqlExtDatabase
from peewee import *

from config import config


POSTGRES_CREDS = config["creds"]["postgres"]
db = PostgresqlExtDatabase(
    POSTGRES_CREDS["name"],
    user=POSTGRES_CREDS["user"],
    password=POSTGRES_CREDS["password"],
    host=POSTGRES_CREDS["host"],
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

    symbols = ManyToManyField(Symbol, backref="articles")
    title = TextField()
    content = TextField(null=True)
    url = TextField(unique=True)
    source = CharField()
    published = DateTimeField()
    found = DateTimeField()

    class Meta:
        database = db


SymbolArticle = Article.symbols.get_through_model()


class OHLCV(Model):

    symbol = ForeignKeyField(Symbol, backref="ohlcvs", null=True)
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
        indexes = ((("symbol", "source", "start", "period"), True),)


class Stat(Model):

    symbol = ForeignKeyField(Symbol, backref="stats", null=True)
    category = CharField()
    name = CharField()
    source = CharField()
    value = DoubleField(null=True)
    svalue = CharField(null=True)
    published = DateTimeField(null=True)
    found = DateTimeField(null=True)
    effected = DateTimeField(null=True)
    period = IntegerField(null=True)

    class Meta:
        database = db
        indexes = ((("symbol", "source", "name", "effected", "period"), True),)


MODELS = [SymbolArticle, Symbol, Article, OHLCV, Stat]
# db.drop_tables(MODELS, cascade=True)
# db.create_tables(MODELS)
