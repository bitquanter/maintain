# coding: utf-8
import datetime
from sqlalchemy import Column, Date, DateTime, Float, Index, Integer, String, Text, Boolean,TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import get_config

cfg = get_config()

__all__ = [
    'SymbolInfo',
    'DbUtil',
]

Base = declarative_base()
metadata = Base.metadata


class SymbolInfo(Base):
    """
    symbol 基础数据
    """
    __tablename__ = 'symbolinfo'
    id = Column(Integer, primary_key=True)
    base_currency = Column(Text, nullable=False, doc="交易的货币")
    quote_currency = Column(Text, nullable=False, doc="本币")
    symbol = Column(Text, nullable=False, doc="symbol")
    exchange = Column(Text, nullable=False, doc="交易所")
    price_precision = Column(Integer, nullable=True, doc='价格精度')
    amount_precision = Column(Integer, nullable=True, doc="数量精度")
    min_amount = Column(Float, nullable=True, doc="最小数量")
    created_at = Column(TIMESTAMP, default=datetime.datetime.now)
    updated_at = Column(TIMESTAMP, default=datetime.datetime.now)


class DbUtil(object):
    def __init__(self):
        self._engine = create_engine(cfg.get_sqlite_db_uri(), echo=False)
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

    def save_symbol_info(self, symbol_info):
        # 查询表中是否已经有该条币对信息
        symbol = self._session.query(SymbolInfo).filter(SymbolInfo.symbol == symbol_info['symbol']).filter(SymbolInfo.exchange == symbol_info['exchange']).first()
        if symbol: # 更新
            if symbol_info['price_precision']:
                symbol.price_precision = symbol_info['price_precision']
            if symbol_info['amount_precision']:
                symbol.amount_precision = symbol_info['amount_precision']
            if symbol_info['min_amount']:
                symbol.min_amount = symbol_info['min_amount']
            self._session.add(symbol)
        else: # 添加
            sym_obj = SymbolInfo(base_currency = symbol_info['base_currency'],
                                 quote_currency = symbol_info['quote_currency'],
                                 symbol = symbol_info['symbol'],
                                 exchange = symbol_info['exchange'],
                                 price_precision = symbol_info['price_precision'],
                                 amount_precision = symbol_info['amount_precision'],
                                 min_amount = symbol_info['min_amount'])
            self._session.add(sym_obj)
        self._session.commit()

    def qry_all_coin_exchange_pair(self):
        coin_ex_pair = self._session.query(SymbolInfo.symbol, SymbolInfo.exchange).all()
        return coin_ex_pair
    
    def qry_all(self):
        return self._session.query(SymbolInfo).all()
