import datetime

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Boolean, Integer, String, Text, ForeignKey, DateTime, UniqueConstraint, Index, func

from sqlalchemy_utc import utcnow
import sys, os
import imp

imp.reload(sys)

HERE = os.path.abspath(__file__)
HOME_DIR = os.path.split(os.path.split(HERE)[0])[0]
os.sys.path.append(HOME_DIR)
# script_path = os.path.join(HOME_DIR, "tools")
from sql_app.database import Base

STRFTIME_FORMAT = "%Y-%m-%d %H:%M:%S"
STRFDATE_FORMAT = "%Y-%m-%d"

class opsLog(Base):
    __tablename__ = 'op_sys_manage_ops_log'
    id = Column(Integer, primary_key=True)
    descname = Column(String(128), nullable=True)  #########模块名称###########
    source = Column(String(64), nullable=True)  ########ip源地址###########
    request = Column(Text, nullable=True)  #######请求参数##########
    response = Column(Text, nullable=True)  ########返回参数###########
    opsmethod = Column(String(64), nullable=True)  ########返回方法##########
    run_time = Column(DateTime, server_default=func.now(), comment="操作时间")

    @property
    def to_dict(self):
        return {"id": self.id, "descname": self.descname, "source": self.source,
                "request": self.request, "response": self.response, "opsmethod": self.opsmethod, "run_time":
                    self.run_time}

class Users(Base):
    __tablename__ = 'op_sys_manage_users'
    id = Column(Integer, primary_key=True)
    username = Column(String(64))
    password_hash = Column(String(1024), nullable=False)
    create_time = Column(DateTime, server_default=func.now(), comment="创建操作时间")
    @property
    def to_dict(self):
        return {"id": self.id, "username": self.username,
                "password_hash": self.password_hash,
                "create_time": self.create_time}

class LarkWebhook(Base):
    __tablename__ = "op_sys_lark_webhook_data"
    id = Column(Integer, primary_key=True)
    business_name = Column(String(16), comment="业务组名称")
    webhook_url = Column(Text, comment="webhook地址")
    used = Column(String(64), nullable=True, comment="用途")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")

    @property
    def to_dict(self):
        return {"id": self.id,  "business_name": self.business_name,  "webhook_url": self.webhook_url, "used": self.used, "create_time": self.create_time}


class LarkAlarmRecord(Base):
    __tablename__ = "lark_alarm_record_data"
    id = Column(Integer, primary_key=True)
    receiver = Column(String(64), comment="接收器")
    status = Column(String(64), comment="状态")
    alerts = Column(Text, nullable=True, comment="告警信息")
    groupLabels = Column(String(64), comment="分组的名称")
    commonLabels = Column(Text, comment="通用标签")
    commonAnnotations = Column(Text, comment="注释标签")
    externalURL = Column(String(64), comment="外部url")
    version = Column(String(12), comment="版本")
    groupKey = Column(String(1024), comment="组标签")
    truncatedAlerts = Column(String(4), comment="阻断报警")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")

    @property
    def to_dict(self):
        return {"id": self.id,
                "receiver": self.receiver,
                "status": self.status,
                "alerts": self.alerts,
                "groupLabels": self.groupLabels,
                "commonLabels": self.commonLabels,
                "commonAnnotations": self.commonAnnotations,
                "externalURL": self.externalURL,
                "version": self.version,
                "groupKey": self.groupKey,
                "truncatedAlerts": self.truncatedAlerts,
                "create_time": self.create_time}


def init_db():
    from database import engine
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    print("ok")
    init_db()
