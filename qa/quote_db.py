# coding: utf-8
import datetime
from sqlalchemy import Column, Date, DateTime, Float, Index, Integer, String, Text, Boolean,TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from os.path import join


OUTPUTS_PATH = '~/'

__all__ = [
    'Bar',
    'DbUtil',
]

Base = declarative_base()
metadata = Base.metadata


class Bar(Base):
    """
    bar数据
    """
    __tablename__ = "bar"
    id = Column(Integer, primary_key=True)
    exchange = Column(Text, nullable=False, doc="交易所")
    symbol = Column(Text, nullable=False, doc="币对")
    freq = Column(Integer, nullable=False, doc="频率")
    open = Column(Float, nullable=True, doc="开盘价")
    close = Column(Float, nullable=True, doc='收盘价')
    high = Column(Float, nullable=True, doc="最高价")
    low = Column(Float, nullable=True, doc="最低价")
    volume = Column(Float, nullable=True, doc="成交数量")
    amount = Column(Float, nullable=True, doc="成交额")
    md_ts = Column(Text, nullable=True, doc="时间")
    created_at = Column(TIMESTAMP, default=datetime.datetime.now)
    updated_at = Column(TIMESTAMP, default=datetime.datetime.now)


class DbUtil(object):
    def __init__(self):
        self._engine = create_engine(join('sqlite:///%s' % (OUTPUTS_PATH), "quote.db"), echo=False)
        Session = sessionmaker(bind=self._engine)
        self._session = Session()
        self.create_db()
        pass

    def create_db(self):
        metadata.create_all(self._engine)
        pass

    def drop_db(self):
        metadata.drop_all(self._engine)
        pass

    def save_bar_data(self, bar):
        bar_obj = Bar(exchange=bar.exchange,
                      symbol=bar.symbol,
                      freq=bar.freq,
                      open=bar.open,
                      close=bar.close,
                      high=bar.high,
                      low=bar.low,
                      volume=bar.volume,
                      amount=bar.amount,
                      md_ts=str(bar.md_ts))
        self._session.add(bar_obj)
        self._session.commit()

