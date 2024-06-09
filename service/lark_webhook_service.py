import json

from sqlalchemy.orm import sessionmaker

from sql_app.database import engine
from sql_app.lark_webhook_db_play import insert_lark_webhook_config, updata_lark_webhook_config, query_lark_webhook_config, query_lark_webhook_id, delete_lark_webhook_config
from sql_app.models import LarkWebhook
from sql_app.ops_log_db_play import insert_ops_bot_log

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()


class LarkWebHookService():
    def create_service(self, data, user_request_data):
        with SessionLocal() as session:
            result_lark_webhook_name = session.query(LarkWebhook).filter_by(business_name=data.get("business_name")).all()
        if result_lark_webhook_name:
            msg = f"LarkWebHook  info: {data.get('business_name')} existing 提示: 已经存在,不允许覆盖操作!"
            return {"code": 1, "data": msg, "message": "Business_name Record already exists", "status": True}
        else:
            insert_db_result_data = insert_lark_webhook_config(data.get("business_name"), data.get("webhook_url"), data.get("used"))
            insert_ops_bot_log("Insert LarkWebHook  app ", json.dumps(user_request_data), "post",
                               json.dumps(insert_db_result_data))
            return insert_db_result_data

    def update_service(self, ID, business_name, webhook_url, used, user_request_data):
        updated_webhook = updata_lark_webhook_config(ID, business_name, webhook_url, used)
        if updated_webhook:
            insert_ops_bot_log("Update webHook deploy app ", json.dumps(user_request_data), "post",
                               json.dumps(updated_webhook))
            return updated_webhook
        return {"code": 50000, "data": "", "message": msg, "status": True}

    def delete_service(self, ID, userRequestData):
        delete_instance = delete_lark_webhook_config(ID)

        if delete_instance:
            insert_ops_bot_log("Delete Lark webhook Deploy App", json.dumps(userRequestData), "delete",
                               json.dumps(delete_instance))
            return delete_instance
        else:
            msg = "Delete Lark webhook failure"
            return {"code": 50000, "data": "", "message": msg, "status": True}

    def query_service(self, page, page_size, business_name, webhook_url):
        """
        1.查询数据
        :param page:
        :param page_size:
        :param business_name:
        :param webhook_url:
        :return:
        """
        return query_lark_webhook_config(page, page_size, business_name, webhook_url)

    def query_service_id(self, Id):
        return query_lark_webhook_id(Id)
