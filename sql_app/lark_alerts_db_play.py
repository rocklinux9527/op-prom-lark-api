import os
from typing import Optional, List, Dict, Any

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import sessionmaker

from sql_app.database import engine
from sql_app.db_play import model_create, model_updateId, model_delete
from sql_app.models import LarkAlarmRecord
from sql_app.models import LarkWebhook
from tools.config import setup_logger, LarkAlarmHeader, LarkWebhookHeader
from fastapi import HTTPException

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
HERE = os.path.abspath(__file__)
HOME_DIR = os.path.split(os.path.split(HERE)[0])[0]
LOG_DIR = os.path.join(HOME_DIR, "logs")


def insert_lark_alert_config(receiver, status, alerts, groupLabels, commonLabels, commonAnnotations, externalURL, version, groupKey, truncatedAlerts):
    """
    1.入参数
    :param receiver:
    :param status:
    :param alerts:
    :param groupLabels:
    :param commonLabels:
    :param commonAnnotations:
    :param externalURL:
    :param version:
    :param groupKey:
    :param truncatedAlerts:
    :return:
    """
    fildes = {
        "receiver": "receiver",
        "status": "status",
        "alerts": "alerts",
        "groupLabels": "groupLabels",
        "commonLabels": "commonLabels",
        "commonAnnotations": "commonAnnotations",
        "externalURL": "externalURL",
        "version": "version",
        "groupKey": "groupKey",
        "truncatedAlerts": "truncatedAlerts"
    }

    request_data = {
        "receiver": receiver,
        "status": status,
        "alerts": alerts,
        "groupLabels": groupLabels,
        "commonLabels": commonLabels,
        "commonAnnotations": commonAnnotations,
        "externalURL": externalURL,
        "version": version,
        "groupKey": groupKey,
        "truncatedAlerts": truncatedAlerts
    }
    return model_create(LarkAlarmRecord, request_data, fildes)


def updata_lark_alert_config(Id, receiver, status, alerts, groupLabels, commonLabels, commonAnnotations, externalURL, version, groupKey, truncatedAlerts):
    """
    1.更新入参参数
    :param Id:
    :param receiver:
    :param status:
    :param alerts:
    :param groupLabels:
    :param commonLabels:
    :param commonAnnotations:
    :param externalURL:
    :param version:
    :param groupKey:
    :param truncatedAlerts:
    :return:
    """
    fildes = {
        "receiver": "receiver",
        "status": "status",
        "alerts": "alerts",
        "groupLabels": "groupLabels",
        "commonLabels": "commonLabels",
        "commonAnnotations": "commonAnnotations",
        "externalURL": "externalURL",
        "version": "version",
        "groupKey": "groupKey",
        "truncatedAlerts": "truncatedAlerts"
    }

    request_data = {
        "receiver": receiver,
        "status": status,
        "alerts": alerts,
        "groupLabels": groupLabels,
        "commonLabels": commonLabels,
        "commonAnnotations": commonAnnotations,
        "externalURL": externalURL,
        "version": version,
        "groupKey": groupKey,
        "truncatedAlerts": truncatedAlerts
    }
    return model_updateId(LarkAlarmRecord, Id, request_data, fildes)


def delete_lark_alert_config(Id):
    """
    1.删除alert record id
    :param Id:
    :return:
    """
    return model_delete(LarkAlarmRecord, Id)


def query_lark_alert_id(id):
    """
    1.id query data
    :param id:
    :return:
    """
    session = SessionLocal()
    data = session.query(LarkAlarmRecord)
    try:
        if id:
            return {"code": 0, "data": data.filter_by(id=id).all(), "messages": "query success", "status": True}
        else:
            return {"code": 0, "data": "", "messages": "Query conditions are not supported", "status": True}
    except Exception as e:
        session.commit()
        session.close()
        return {"code": 1, "data": str(e), "messages": "query failed ", "status": False}

def query_lark_alert_config(page, page_size, receiver=None, status=None, externalURL=None):
    """
    1.实现根据参数参训和分页查询
    """
    session = SessionLocal()
    data = session.query(LarkAlarmRecord)

    if receiver:
        data = data.filter_by(receiver=receiver)
    if status:
        data = data.filter_by(status=status)
    if externalURL:
        data = data.filter_by(externalURL=externalURL)
    try:
        if page and page_size:
            total_count = data.count()
            result_data = data.limit(page_size).offset((page - 1) * page_size).all()
            return {"code": 20000, "total": total_count, "data": jsonable_encoder(result_data),
                    "messages": "query data alarm record success", "status": True, "columns": LarkAlarmHeader}
        else:
            return {"code": 20000, "total": len([i.to_dict for i in data]), "data": jsonable_encoder(data.all()),
                    "messages": "query data alarm record success", "status": True, "columns": LarkAlarmHeader}
    except Exception as e:
        print(e)
        session.commit()
        session.close()
        return {"code": 50000, "total": 0, "data": [i.to_dict for i in data], "messages": "query fail", "status": True,
                "columns": LarkAlarmHeader}

def query_leak_webhook(group: str) -> Dict[str, Any]:
    """
    查询webhook
    :param group: business_name 用于过滤 LarkWebhook 表中的数据
    :return: 包含查询结果的字典
    """
    session = SessionLocal()
    try:
        data = session.query(LarkWebhook)
        if group:
            data = data.filter_by(business_name=group)
        result = data.all()
        if not result:
            return {"code": 40000, "message": "No data found for the given group", "status": False}
        webhook_urls = [item.webhook_url for item in result]
        return {
            "code": 20000,
            "total": len(webhook_urls),
            "data": jsonable_encoder(webhook_urls),
            "message": "Query data leak_webhook success",
            "status": True,
            "columns": LarkWebhookHeader
        }
    except Exception as e:
        session.rollback()
        return {
            "code": 50000,
            "total": 0,
            "data": "",
            "message": "Query data leak_webhook fail",
            "status": True,
            "columns": LarkWebhookHeader
        }
    finally:
        session.close()


