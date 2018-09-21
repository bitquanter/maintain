# coding: utf-8
import datetime
from sqlalchemy import Column, Date, DateTime, Float, Index, Integer, String, Text, Boolean,TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import get_config
from redis_monitor import get_all_data


cfg = get_config()

__all__ = [
    'FundIndexRawStaticData',
    'FundIndexRawDynamicData',
    'FundIndex',
    'DbUtil',
]

Base = declarative_base()
metadata = Base.metadata


class FundIndexRawStaticData(Base):
    """
    指数所需静态基础数据
    """
    __tablename__ = 'fund_index_raw_static_data'
    id = Column(Integer, primary_key=True)
    sample_time = Column(Text, nullable=False, doc="")
    name = Column(Text, nullable=False, doc="")
    updated_at = Column(Text, nullable=True, doc="")
    float_ = Column(Text, nullable=True, doc="")
    updater = Column(Integer, nullable=True, doc="")
    flag = Column(Integer, nullable=True, doc="")
    memo = Column(Float, nullable=True, doc="")
    created_at = Column(TIMESTAMP, default=datetime.datetime.now)
    updated_at = Column(TIMESTAMP, default=datetime.datetime.now)


class FundIndexRawDynamicData(Base):
    """
    指数所需动态基础数据
    """
    __tablename__ = 'fund_index_raw_dynamic_data'
    id = Column(Integer, primary_key=True)
    sample_time = Column(DateTime, nullable=False, doc="")
    name = Column(Text, nullable=False, doc="")
    data = Column(Text, nullable=True, doc="")
    # updated_at = Column(Text, nullable=True, doc="")
    # float_ = Column(Text, nullable=True, doc="")
    # updater = Column(Integer, nullable=True, doc="")
    # flag = Column(Integer, nullable=True, doc="")
    # memo = Column(Float, nullable=True, doc="")
    created_at = Column(TIMESTAMP, default=datetime.datetime.now)
    updated_at = Column(TIMESTAMP, default=datetime.datetime.now)


class FundIndex(Base):
    """
    所有基金计算值
    """
    __tablename__ = 'fund_index'
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False, doc="")
    sample_time_stamp = Column(Text, nullable=False, doc="")
    actual_time = Column(Text, nullable=False, doc="")
    float_ = Column(Text, nullable=False, doc="")
    updater = Column(Integer, nullable=True, doc='')
    flag = Column(Integer, nullable=True, doc="")
    memo = Column(Float, nullable=True, doc="")
    created_at = Column(TIMESTAMP, default=datetime.datetime.now)
    updated_at = Column(TIMESTAMP, default=datetime.datetime.now)


class TickMonitor(Base):
    """
    监控redis记录状态
    """
    __tablename__ = 'tick_monitor'
    id = Column(Integer, primary_key=True)
    key_name = Column(Text, nullable=False, doc="")
    value = Column(Text, nullable=True, doc="")
    time = Column(TIMESTAMP, default=datetime.datetime.now)
        


class DbUtil(object):
    def __init__(self):
        self._engine = create_engine(cfg.get_sqlite_db_uri(), echo=False)
        Session = sessionmaker(bind=self._engine)
        self._session = Session()
        # self.drop_db()
        self.create_db()
        pass

    def create_db(self):
        metadata.create_all(self._engine)
        pass

    def drop_db(self):
        metadata.drop_all(self._engine)
        pass

    def gen_next_day_placeholder(self, exchang_coin_list, time_list):
        count = self._session.query(FundIndexRawDynamicData).filter(FundIndexRawDynamicData.name.in_(exchang_coin_list)).filter(FundIndexRawDynamicData.sample_time.in_(time_list)).count()
        print('count:', count)
        if count == len(exchang_coin_list) * len(time_list):
            return
        self._session.query(FundIndexRawDynamicData).filter(FundIndexRawDynamicData.name.in_(exchang_coin_list)).filter(FundIndexRawDynamicData.sample_time.in_(time_list)).delete(synchronize_session=False)
        self._session.commit()
        for exc in exchang_coin_list:
            for t in time_list:
                obj = FundIndexRawDynamicData(name=exc,sample_time=t)
                self._session.add(obj)
        self._session.commit()
        pass

    def update_fund_dynamic_data(self, data):
        for d in data:
            upd = self._session.query(FundIndexRawDynamicData).filter(FundIndexRawDynamicData.name==d['name']).filter(FundIndexRawDynamicData.sample_time==d['time']).first()
            print(upd)
            if upd is not None:
                upd.data = str(d['data'])
                self._session.add(upd)
                self._session.commit()

    def write_tick_monitor(self, data):
        for d in data:
            obj = TickMonitor(key_name=d['key'], value=d['value'], time=d['time'])
            self._session.add(obj)
        self._session.commit()
        pass


db = DbUtil()

def write_to_db():
    data = get_all_data()
    db.write_tick_monitor(data)
    pass
