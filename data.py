# -*- coding: UTF-8 –*-
import time

from sqlalchemy import *
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, mapper, relationship

from utilities import generateGUID

import datetime

year = time.strftime('%Y',time.localtime(time.time()))#获取当前年
#print year
playplantable = "t_PlayPlan" + year
compareresulttable = 't_CompareResult' + year
feedbacktable = 't_FeedBack' + year




# 初始化数据库连接:
host = '10.5.6.101'
ADdb = 'ORAADM'
ACdb = 'AudioClipperDB'
user='infos1'
password='20030102'
charset="utf8"



def db(host, database, user,password,charset):
    engine = create_engine('mssql+pymssql://' + user + ':' + password + '@' + host + ':1433/' + database, encoding=charset)
    return engine


"""
连接广告监播数据库并映射相关表

"""
# 连接ADmonitor数据库
ADengine = db(host, ADdb, user, password, charset)
ADmetadata = MetaData()
ADmetadata.reflect(ADengine, only=[playplantable, 't_Channel', 't_PlayPlanType', 't_FeedBackType', 't_CompactType', compareresulttable, feedbacktable])
ADBase = automap_base(metadata=ADmetadata)
ADBase.prepare()


# 映射t_PlayPlan表
AD_PlayPlan = ADBase.classes.t_PlayPlan2018

# 映射t_Channel表
AD_Channel = ADBase.classes.t_Channel

# 映射t_FeedBackType
AD_FeedBackType = ADBase.classes.t_FeedBackType

# 映射t_PlayPlanType表
AD_PlayPlanType = ADBase.classes.t_PlayPlanType

# 映射t_CompactType表
AD_CompactType = ADBase.classes.t_CompactType

# 映射t_CompareResult表
AD_CompareResult = ADBase.classes.t_CompareResult2018

# 映射t_FeedBack表
AD_FeedBack = ADBase.classes.t_FeedBack2018


# 定义口播广告对应关键词表
class PlayPlanKeyword(ADBase):
    __tablename__ = 't_PlayPlanKeyword' + year
    id = Column('s_PlayPlanKeywordGuid', default=generateGUID(), primary_key=True)
    keywords = Column('s_Keywords', VARCHAR, )


# 定义音频处理结果表
class LoggerSegment(ADBase):
    __tablename__ = 't_LoggerSegment'
    id = Column('s_LoggerSegmentGuid', default=generateGUID(), primary_key=True)


# 定义语音转写结果表
class LfasrRecord(ADBase):
    __tablename__ = 't_LfasrRecord'
    id = Column('s_LfasrRecordGuid', default=generateGUID(), primary_key=True)


"""
查询广告监播数据库

"""
def QueryStationID(ChannelGUID):
    # 创建DBSession类型:
    DBSession = sessionmaker(bind=ADengine)
    session = DBSession()

    channel = session.query(AD_Channel).filter(AD_Channel.s_ChannelGUID == ChannelGUID).one()
    session.close()
    return channel.i_ChannelID


def QueryPlayPlan(date, typeguid):
    # 创建DBSession类型:
    DBSession = sessionmaker(bind=ADengine)
    session = DBSession()
    playplanlist = session.query(AD_PlayPlan)\
        .filter(and_(AD_PlayPlan.d_PlayPlanPlayDate == date, AD_PlayPlan.s_PlayPlanTypeGuid == typeguid))\
        .order_by(AD_PlayPlan.s_PlayPlanStartTime.asc())\
        .all()
    session.close()
    return playplanlist


def QueryPlayPlanType(name):
    # 创建DBSession类型:
    DBSession = sessionmaker(bind=ADengine)
    session = DBSession()
    OAAd = session.query(AD_PlayPlanType).filter(AD_PlayPlanType.s_PlayPlanTypeName == name).one()
    session.close()
    return OAAd.s_PlayPlanTypeGuid


"""
连接切分数据库并映射相关表

"""
# 连接ADmonitor数据库
ACengine = db(host, ACdb, user, password, charset)
ACmetadata = MetaData()
ACmetadata.reflect(ACengine, only=['Channels', 'Packets', 'Programs', 'ProgramNoads', 'Folders'])
ACBase = automap_base(metadata=ACmetadata)
ACBase.prepare()

# 映射Channels表
AC_Channel = ACBase.classes.Channels


# 映射Packets表
AC_Packets = ACBase.classes.Packets


# 映射Programs表
AC_Programs = ACBase.classes.Programs


# 映射ProgramsNoads表
AC_ProgramNoads = ACBase.classes.ProgramNoads


# 映射Folders表
AC_Folders = ACBase.classes.Folders


"""
查询切分数据库

"""
def QueryChannelID(StationID):
    # 创建DBSession类型
    DBSession = sessionmaker(bind=ACengine)
    session = DBSession()

    channel = session.query(AC_Channel).filter(AC_Channel.StationID == StationID).one()
    session.close()
    return channel.ChannelID


def QueryKeyWords(playplanguid):
    # 创建DBSession类型
    DBSession = sessionmaker(bind=ADengine)
    session = DBSession()

    keywords = session.query(AD_PlayPlan)\
               .filter(AD_PlayPlan.s_PlayPlanGuid == playplanguid)\
               .one().s_PlayPlanScriptName
    session.close()

    return keywords


def QueryFilePath(program, count):
    # 创建DBSession类型
    DBSession = sessionmaker(bind=ACengine)
    session = DBSession()
    mp3Files = []
    pros = []

    while len(pros) < count:
        # files = session.query(AC_ProgramNoads).filter(AC_ProgramNoads.StartTime >= str(yesterday) + " 00:00:00.000").all()
        for p in program:
            file = session.query(AC_ProgramNoads).filter(AC_ProgramNoads.ProgramID == p["ProgramID"]).one_or_none()
            if file:
                if p["ProgramID"] not in pros:
                    pros.append(p["ProgramID"])
                    playplanguid = p["Desciption"]
                    keywords = QueryKeyWords(playplanguid)
                    mp3Files.append({"filepath": file.FilePath, "keywords": keywords})
                    print "完成1条：" + str(file.FilePath) + " 关键词为：" + str(keywords)
        print "共" + str(count) + "条， " + "已完成" + str(len(mp3Files)) + "条"
        time.sleep(60)
    session.close()


    return mp3Files


def QueryFilePath2(yesterday, count):
    # 创建DBSession类型
    DBSession = sessionmaker(bind=ACengine)
    session = DBSession()
    mp3Files = []

    while len(mp3Files) < count:
        files = session.query(AC_ProgramNoads).filter(AC_ProgramNoads.StartTime >= str(yesterday) + " 00:00:00.000").all()
        for p in files:
            pro = session.query(AC_Programs).filter(AC_Programs.ProgramID == p.ProgramID).one_or_none()
            if pro:
                playplanguid = pro.Desciption
                keywords = QueryKeyWords(playplanguid)
                mp3Files.append({"filepath": p.FilePath, "keywords": keywords})
                print "完成1条：" + str(p.FilePath) + " 关键词为：" + str(keywords)
        print "共" + str(count) + "条， " + "已完成" + str(len(mp3Files)) + "条"

    session.close()


    return mp3Files












# TODO
"""
# 查询所有口播计划
输入：日期、口播类型GUID
返回：当天所有口播PlayPlan
"""


def GetPlayPlan(yesterday, PlayPlanTypeGuid):
    ydatetime = datetime.datetime.combine(yesterday, datetime.time.min)

    # 查询当天的所有口播计划
    PlayPlanList = QueryPlayPlan(ydatetime, PlayPlanTypeGuid)
    for playplan in PlayPlanList:
        print QueryStationID(playplan.s_ChannelGUID) \
            , playplan.s_PlayPlanStartTime \
            , playplan.s_PlayPlanEndTime \
            , playplan.s_PlayPlanAdName
    print "共" + str(len(PlayPlanList)) + "条"
    return PlayPlanList, len(PlayPlanList)


# TODO
"""
# 将PlayPlan写入切分数据库
输入：一条PlayPlan （ Channel的GUID -> Channel的编号 、时间段、相关节目
返回：一条Packet （Channel的编号 -> Channel的GUID、相关节目）和 一条Program（PacketID、时间段、相关节目、ProgramType = 0）
"""

def SetAudioClipper(yesterday, PlayPlanList):
    print "写入音频切分数据库..."
    Packet = []
    Program = []
    Folder = []
    for playplan in PlayPlanList:
        stationID = QueryStationID(playplan.s_ChannelGUID)
        # print "stationID: " + str(stationID)
        AC_ChannelID = QueryChannelID(stationID)
        PacketName = playplan.s_PlayPlanPacketName
        playplanguid = playplan.s_PlayPlanGuid
        FolderName = PacketName
        PacketID = generateGUID()
        # 获取昨天周几
        yweek = yesterday.weekday() + 1
        DayOfWeek = yweek
        FolderID = generateGUID()
        StartTime = str(yesterday) + " " + playplan.s_PlayPlanStartTime
        EndTime = str(yesterday) + " " + playplan.s_PlayPlanEndTime
        ProgramID = generateGUID()
        ProgramName = PacketName + " [" + StartTime + "]"
        ProgramType = 0
        AddDateTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        Packet.append({'PacketID': PacketID,
                       'ChannelID': AC_ChannelID,
                       'PacketName': PacketName,
                       'DayOfWeek': DayOfWeek,
                       'StartTime': StartTime,
                       'EndTime': EndTime,
                       'FolderID': FolderID
        })
        Program.append({
            'ProgramID': ProgramID,
            'PacketID': PacketID,
            'Desciption': playplanguid,
            'StartTime': StartTime,
            'EndTime': EndTime,
            'ProgramName': ProgramName,
            'ProgramType': ProgramType,
            'AddDateTime': AddDateTime
        })
        Folder.append({
            'FolderID': FolderID,
            'ChannelID': AC_ChannelID,
            'FolderName': FolderName
        })

    # print Packet
    # print Program
    # print Folder

    conn = ACengine.connect()
    i1 = AC_Packets.__table__.insert()
    p1 = conn.execute(i1, Packet)

    i2 = AC_Programs.__table__.insert()
    p2 = conn.execute(i2, Program)

    i3 = AC_Folders.__table__.insert()
    p3 = conn.execute(i3, Folder)
    print "等待音频切分...\n"

    return Program


def GetAudioClipper(Program):
    MP3List = []
    for p in Program:
        audioFile = QueryFilePath(p["ProgramID"])
        MP3List.append(audioFile)
    return MP3List




# TODO
"""
# 将FeedBack写入FeedBack
"""

# TODO
"""
# 将FeedBack写入CompareResult
"""






