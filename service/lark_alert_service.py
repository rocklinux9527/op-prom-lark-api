import json

from sqlalchemy.orm import sessionmaker

from sql_app.database import engine
from sql_app.lark_alerts_db_play import insert_lark_alert_config, updata_lark_alert_config, query_lark_alert_config, \
    query_lark_alert_id, delete_lark_alert_config, query_leak_webhook
from sql_app.lark_webhook_db_play import query_lark_webhook_config
from sql_app.models import LarkAlarmRecord

from sql_app.ops_log_db_play import insert_ops_bot_log
# from tools.config import  send_lark_webhook_url

from tools.lark_send import send_lark_alert
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()


class LarkAlertService():
    def alert_send_to_lark(self, data, webhook_url):
        return send_lark_alert(data, webhook_url)

    def create_alert_service(self, data, user_request_data):
        print(type(data))
        try:
            # # 打印每个数据的类型和内容以调试
            # print(f"receiver: {type(data.get('receiver'))} - {data.get('receiver')}")
            # print(f"status: {type(data.get('status'))} - {data.get('status')}")
            # print(f"alerts: {type(data.get('alerts'))} - {data.get('alerts')}")
            # print(f"groupLabels: {type(data.get('groupLabels'))} - {data.get('groupLabels')}")
            # print(f"commonLabels: {type(data.get('commonLabels'))} - {data.get('commonLabels')}")
            # print(f"commonAnnotations: {type(data.get('commonAnnotations'))} - {data.get('commonAnnotations')}")
            # print(f"externalURL: {type(data.get('externalURL'))} - {data.get('externalURL')}")
            # print(f"version: {type(data.get('version'))} - {data.get('version')}")
            # print(f"groupKey: {type(data.get('groupKey'))} - {data.get('groupKey')}")
            # print(f"truncatedAlerts: {type(data.get('truncatedAlerts'))} - {data.get('truncatedAlerts')}")
            receiver = json.dumps(data.get("receiver"))
            status = json.dumps(data.get("status"))
            alerts = json.dumps(data.get("alerts"))
            groupLabels = json.dumps(data.get("groupLabels"))
            commonLabels = json.dumps(data.get("commonLabels"))
            commonAnnotations = json.dumps(data.get("commonAnnotations"))
            externalURL = str(data.get("externalURL"))
            version = json.dumps(data.get("version"))
            groupKey = json.dumps(data.get("groupKey"))
            truncatedAlerts = json.dumps(data.get("truncatedAlerts"))

            insert_db_result_data = insert_lark_alert_config(
                receiver,
                status,
                alerts,
                groupLabels,
                commonLabels,
                commonAnnotations,
                externalURL,
                version,
                groupKey,
                truncatedAlerts
            )
            insert_ops_bot_log("Insert LarkAlert  AlarmRecord", json.dumps(user_request_data),
                               "post", json.dumps(insert_db_result_data))
            return insert_db_result_data
        except Exception as e:
            print(str(e))
            return {"code": 50000, "data": "", "message": str(e), "status": True}

    def update_alert_service(self, data, user_request_data):
        updated_alert = updata_lark_webhook_config(ID,
                                                   data.get("receiver"),
                                                   data.get("status"),
                                                   data.get("alerts"),
                                                   data.get("groupLabels"),
                                                   data.get("commonLabels"),
                                                   data.get("commonAnnotations"),
                                                   data.get("externalURL"),
                                                   data.get("version"),
                                                   data.get("groupKey"),
                                                   data.get("truncatedAlerts")
                                                   )
        if updated_webhook:
            insert_ops_bot_log("Update LarkAlert  AlarmRecord", json.dumps(user_request_data), "post",
                               json.dumps(updated_webhook))
            return updated_alert
        return {"code": 50000, "data": "", "message": msg, "status": True}

    def delete_alert_service(self, ID, userRequestData: dict):
        delete_instance = delete_lark_alert_config(ID)

        if delete_instance:
            insert_ops_bot_log("Delete Lark Alert Record", json.dumps(userRequestData), "delete",
                               json.dumps(delete_instance))
            return delete_instance
        else:
            msg = "Delete Lark Alert Record failure"
            return {"code": 50000, "data": "", "message": msg, "status": True}

    def query_alert_service(self, page, page_size, receiver, status, externalURL):
        """
        1.查询数据
        :param page:
        :param page_size:
        :param business_name:
        :param webhook_url:
        :return:
        """
        return query_lark_alert_config(page, page_size, receiver, status, externalURL)

    def query_alert_id(self, Id):
        return query_lark_webhook_id(Id)

    def query_lark_webhook_address(self, data):
        data = query_leak_webhook(data)
        return data

    def query_all_lark_webhook(self):
        page = 1
        page_size = 1000
        try:
            query_webhook_all = query_lark_webhook_config(page=page, page_size=page_size)
        except Exception as e:
            return {"code": 50000, "data": "", "message": f"查询 webhook 配置时发生错误: {str(e)}", "status": False}

        data_list = query_webhook_all.get("data", [])
        if not data_list:
            return {"code": 50000, "data": "", "message": "业务线和webhook未配置,请提前配置...", "status": True}
        business_names = [item["business_name"] for item in data_list]
        return {"code": 20000, "data": business_names, "message": "query business_name list success", "status": True}
