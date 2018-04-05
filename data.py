# -*- coding: UTF-8 –*-
import time

from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, mapper, relationship

from utilities import generateGUID

year = time.strftime('%Y',time.localtime(time.time()))#获取当前年
print year




# 初始化数据库连接:
host = '10.5.6.101'
database='ORAADM'
user='admxp'
password='admxp0701'
charset="utf8"


ChannelGUID = '5848cf20-45f7-417b-a6dd-2fef75744b81'


def db(host, database, user,password,charset):
    engine = create_engine('mssql+pymssql://' + user + ':' + password + '@' + host + ':1433/' + database, echo=True, encoding=charset)
    return engine




engine = db(host, database, user, password, charset)
engine.echo = True  # We want to see the SQL we're creating
metadata = MetaData(engine)


# 映射t_Channel表
Channels = Table('t_Channel', metadata, autoload=True)
class Channel(object):
    pass
channelmapper = mapper(Channel, Channels)


# 映射t_PlayPlan表
PlayPlans = Table('t_PlayPlan' + year, metadata, autoload=True)
class PlayPlan(object):
    pass
PlayPlanmapper = mapper(PlayPlan, PlayPlans)


# 映射t_FeedBackType
FeedBackTypes = Table('t_FeedBackType', metadata, autoload=True)
class FeedBackType(object):
    pass
FeedBackTypemapper = mapper(FeedBackType, FeedBackTypes)


# 映射t_PlayPlanType表
PlayPlanTypes = Table('t_PlayPlanType', metadata, autoload=True)
class PlayPlanType(object):
    pass
PlayPlanTypemapper = mapper(PlayPlanType, PlayPlanTypes)


# 映射t_CompactType表
CompactTypes = Table('t_CompactType', metadata, autoload=True)
class CompactType(object):
    pass
CompactTypemapper = mapper(CompactType, CompactTypes)


# 映射t_CompareResult表
CompareResults = Table('t_CompareResult', metadata, autoload=True)
class CompareResult(object):
    pass
CompareResultmapper = mapper(CompareResult, CompareResults)


# 映射t_FeedBack表
FeedBacks = Table('t_FeedBack' + year, metadata, autoload=True)
class FeedBack(object):
    pass
FeedBackmapper = mapper(FeedBack, FeedBacks)


# 创建对象的基类:
Base = declarative_base()


# 定义口播广告对应关键词表
class PlayPlanKeyword(Base):
    __tablename__ = 't_PlayPlanKeyword' + year
    id = Column('s_LoggerSegmentGuid', default=generateGUID(), primary_key=True)
    keywords = Column('s_Keywords', VARCHAR, )

    playplan_id = Column(Integer, ForeignKey('PlayPlan.s_PlayPlanGuid'))
    playplan = relationship("PlayPlan")


# 定义音频处理结果表
class LoggerSegment(Base):
    __tablename__ = 't_LoggerSegment'
    id = Column('s_LoggerSegmentGuid', default=generateGUID(), primary_key=True)


# 定义语音转写结果表
class LfasrRecord(Base):
    __tablename__ = 't_LfasrRecord'
    id = Column('s_LfasrRecordGuid', default=generateGUID(), primary_key=True)

def QueryChannelName(ChannelGUID, engine):
    # 创建DBSession类型:
    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    channel = session.query(Channel).filter(Channel.s_ChannelGUID == ChannelGUID).one()
    session.close()
    return channel.s_ChannelName


print QueryChannelName(ChannelGUID, engine)










