from sql_app.db_play import model_create, model_update, model_updateId, model_delete
from sql_app.models import LarkWebhook
from sqlalchemy.orm import sessionmaker
from sql_app.database import engine
from sqlalchemy import and_
from typing import Optional
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from tools.config import setup_logger, LarkWebhookHeader
import os

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
HERE = os.path.abspath(__file__)
HOME_DIR = os.path.split(os.path.split(HERE)[0])[0]
LOG_DIR = os.path.join(HOME_DIR, "logs")


def insert_lark_webhook_config(business_name, webhook_url, used):
    """
    1.新增入库参数
    :param business_name:
    :param webhook_url:
    :param used:
    :return:
    """
    fildes = {
        "business_name": "business_name",
        "webhook_url": "webhook_url",
        "used": "used"
    }

    request_data = {
        "business_name": business_name,
        "webhook_url": webhook_url,
        "used": used
    }
    return model_create(LarkWebhook, request_data, fildes)


def updata_lark_webhook_config(Id, business_name, webhook_url, used):
    """
    1.修改kube config 配置入库
    :param Id:
    :param business_name:
    :param webhook_url:
    :param used:
    :return:
    """
    fildes = {
        "business_name": "business_name",
        "webhook_url": "webhook_url",
        "used": "used"
    }

    request_data = {
        "business_name": business_name,
        "webhook_url": webhook_url,
        "used": used
    }
    return model_updateId(LarkWebhook, Id, request_data, fildes)


def delete_lark_webhook_config(Id):
    """
    1.删除kube config 配置入库
    :param Id:
    :return:
    """
    return model_delete(LarkWebhook, Id)


def query_lark_webhook_id(id):
    """
    1.id query data
    :param id:
    :return:
    """
    session = SessionLocal()
    data = session.query(LarkWebhook)
    try:
        if id:
            return {"code": 0, "data": data.filter_by(id=id).all(), "messages": "query success", "status": True}
        else:
            return {"code": 0, "data": "", "messages": "Query conditions are not supported", "status": True}
    except Exception as e:
        session.commit()
        session.close()
        return {"code": 1, "data": str(e), "messages": "query failed ", "status": False}


def query_lark_webhook_config(page: int = 1, page_size: int = 10, business_name: Optional[str] = None,
                              webhook_url: Optional[str] = None):
    """
    1.根据不同条件查询配置信息
    """
    session = SessionLocal()
    query = session.query(LarkWebhook)
    try:
        if business_name:
            query = query.filter(LarkWebhook.business_name == business_name)
        if webhook_url:
            query = query.filter(LarkWebhook.webhook_url == webhook_url)
        data = query.limit(page_size).offset((page - 1) * page_size).all()
        total = query.count()
        return {"code": 20000, "total": total, "data": jsonable_encoder(data), "messages": "query data success", "status": True,
                "columns": LarkWebhookHeader}
    except Exception as e:
        logger = setup_logger()
        logger.info("Lark webhook query config error  ", extra={'props': {"message": str(e)}})
        return {"code": 50000, "total": 0, "data": "query data failure ", "messages": str(e), "status": True,
                "columns": LarkWebhookHeader}


def query_lark_webhook_config(page, page_size, business_name=None, webhook_url=None):
    """
    """
    session = SessionLocal()
    data = session.query(LarkWebhook)
    # 根据参数进行查询
    if business_name:
        data = data.filter_by(business_name=business_name)
    if webhook_url:
        data = data.filter_by(webhook_url=webhook_url)
    try:
        if page and page_size:
            total_count = data.count()
            result_data = data.limit(page_size).offset((page - 1) * page_size).all()
            return {"code": 20000, "total": total_count, "data": jsonable_encoder(result_data),
                    "messages": "query data success", "status": True, "columns": LarkWebhookHeader}
        else:
            return {"code": 20000, "total": len([i.to_dict for i in data]), "data": jsonable_encoder(data.all()),
                    "messages": "query data success", "status": True, "columns": LarkWebhookHeader}
    except Exception as e:
        print(e)
        session.commit()
        session.close()
        return {"code": 50000, "total": 0, "data": [i.to_dict for i in data], "messages": "query success fail", "status": True,
                "columns": LarkWebhookHeader}
