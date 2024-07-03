import logging
from logging.handlers import TimedRotatingFileHandler
from typing import List, Dict, Any, Optional
import json
import json_logging
# login token
import uvicorn
from fastapi import APIRouter, Query
from fastapi import FastAPI
from pydantic import ValidationError
from starlette.middleware.cors import CORSMiddleware
from fastapi import Request, HTTPException, Body

# Lark BaseModel
from schemas.lark import AlertItem, SendLarkWebhook, CreateWebhookItem, UpdateWebhookItem, DeleteWebhookItem
from tools.config import access_log_filename

# import mysql db connection check
from service.check_mysql_conn import check_mysql_connection

# import webhook lark service

from service.lark_webhook_service import LarkWebHookService

# db ops deploy and ops logs
from sql_app.ops_log_db_play import query_operate_ops_log

# import webhook lark LarkAlertService
from service.lark_alert_service import LarkAlertService

app_name = "op-prom-lark-api"
app = FastAPI(
    title=app_name,
    description="Alert-manager To Lark-webhook API 工具",
    version="0.0.1",
)

# 初始化和fastapi 关联
json_logging.init_fastapi(enable_json=True)
json_logging.init_request_instrument(app)
router = APIRouter()

origins = ["*", "127.0.0.1:80"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/check-mysql", summary="mysql db connection heck ", tags=["mysql-check"])
async def check_mysql():
    result = await check_mysql_connection()
    return result


@app.get("/api/sys/ops/log/v1", summary="排查问题-参数请求日志", tags=["ops_logs_list"])
def get_sys_ops_log(descname: Optional[str] = None, request: Optional[str] = None):
    return query_operate_ops_log(descname, request)


@app.get("/api/v1/all-lark-webhooks", summary="Get namespace App All Plan", tags=["WebhookLark-all"])
def get_lark_webhook_plan(page: int = Query(1, gt=0), page_size: int = Query(10, gt=0, le=100), receiver: Optional[str] = None,
                          status: Optional[str] = None, externalURL: Optional[str] = None):
    LarkAlertInstance = LarkAlertService()
    results = LarkAlertInstance.query_alert_service(page, page_size, receiver, status, externalURL)
    return results


@app.post("/api/v1/all-lark-webhooks", summary="send lark all webhook api", tags=["WebhookLark-all"])
async def post_to_all_lark_webhooks(group: str, request: Request, request_data: SendLarkWebhook = Body(..., examples={
    "example1": {
        "summary": "An example of request body",
        "value": {
            "receiver": "default-receiver",
            "status": "firing",
            "alerts": [
                {
                    "status": "firing",
                    "labels": {
                        "alertname": "KubePodNotReady",
                        "namespace": "default",
                        "pod": "example-app-f4fddc88-ndtf6",
                        "prometheus": "monitoring/prometheus-stack-kube-prom-prometheus",
                        "severity": "warning",
                        "container": "kube-state-metrics",
                        "endpoint": "http",
                        "instance": "10.244.36.80:8080",
                        "job": "kube-state-metrics",
                        "phase": "Pending",
                        "service": "prometheus-stack-kube-state-metrics",
                        "uid": "7b626232-5e22-4db9-8f6c-ba1fed705344"
                    },
                    "annotations": {
                        "description": "Pod default/example-app-f4fddc88-ndtf6 has been in a non-ready state for longer than 15 minutes.",
                        "summary": "Pod has been in a non-ready state for more than 15 minutes."
                    },
                    "startsAt": "2024-06-05T14:02:51.531Z",
                    "endsAt": "0001-01-01T00:00:00Z",
                    "generatorURL": "https://runbooks.prometheus-operator.dev/runbooks/general/targetdown",
                    "fingerprint": "2dca31ec35b4c5d5"
                }
            ],
            "groupLabels": {
                "alertname": "KubePodNotReady"
            },
            "commonLabels": {
                "alertname": "KubePodNotReady",
                "namespace": "default",
                "pod": "example-app-f4fddc88-ndtf6",
                "prometheus": "monitoring/prometheus-stack-kube-prom-prometheus",
                "severity": "warning",
                "container": "kube-state-metrics",
                "endpoint": "http",
                "instance": "10.244.36.80:8080",
                "job": "kube-state-metrics",
                "phase": "Pending",
                "service": "prometheus-stack-kube-state-metrics",
                "uid": "7b626232-5e22-4db9-8f6c-ba1fed705344"
            },
            "commonAnnotations": {
                "description": "Pod default/example-app-f4fddc88-ndtf6 has been in a non-ready state for longer than 15 minutes.",
                "summary": "Pod has been in a non-ready state for more than 15 minutes."
            },
            "externalURL": "http://alertmanager.k8s.local",
            "version": "4",
            "groupKey": "{}:{alertname=\"KubePodNotReady\"}",
            "truncatedAlerts": 0
        }
    }
})):
    LarkAlertInstance = LarkAlertService()
    data = request_data.dict()
    user_request_data = await request.json()
    print("alertManager 请求来了",user_request_data)
    if not (group):
        raise HTTPException(status_code=400, detail="业务线和webhook未配置,请提前配置")
    queryLarkWebhookList = LarkAlertInstance.query_all_lark_webhook()

    if queryLarkWebhookList.get("code") == 20000:
        data_list = queryLarkWebhookList.get("data", [])
    if group in data_list:
        WebHookGroupResult = LarkAlertInstance.query_lark_webhook_address(group)
        if WebHookGroupResult.get("code") != 20000:
            raise HTTPException(status_code=400, detail="Failed to query webhook addresses")
        webhook_urls_list = []
        for webhook_urls_str in WebHookGroupResult['data']:
            webhook_urls_list.extend(webhook_urls_str.split(','))
        success_count = 0
        failure_count = 0

        for webhook_url in webhook_urls_list:
            try:
                results = LarkAlertInstance.alert_send_to_lark(data, webhook_url)
                for result in results:
                    if result.get("code") == 20000:
                        success_count += 1
                    elif result.get("code") == 50000:
                        failure_count += 1
            except ValidationError as e:
                raise HTTPException(status_code=400, detail=str(e))

        if success_count > 0:
            LarkAlertSQlInstance = LarkAlertService()
            sqlResult = LarkAlertSQlInstance.create_alert_service(data, user_request_data)
            return {"code": "20000", "message": "Request data received successfully", "status": True}
        elif failure_count > 0:
            return {"code": "50000", "message": "Request all data received failure", "status": False}
        else:
            return {"code": "30000", "message": "Partial success", "status": True}
    else:
        raise HTTPException(status_code=400, detail="业务线: {data} 未定义,请提前配置.....".format(data=group))


@app.get("/api/v1/webhook", summary="get webhook plan ", tags=["Webhook-Item"])
def get_webhook_list(page: int = Query(1, gt=0), page_size: int = Query(10, gt=0, le=100), business_name: Optional[str] = None,
                     webhook_url: Optional[str] = None):
    lark_webhook_instance = LarkWebHookService()
    result_data = lark_webhook_instance.query_service(page, page_size, business_name, webhook_url)
    return result_data


@app.post("/api/v1/webhook", summary="Add Webhook Plan", tags=["Webhook-Item"])
async def create_webhook_config(request: Request, request_data: CreateWebhookItem):
    user_request_data = await request.json()
    data = request_data.dict()
    if not all(data.get(field) for field in
               ['business_name', 'webhook_url', 'used']):
        return {'code': 20000, 'messages': "If the parameter is insufficient, check it", "data": "", "status": False}
    lark_webhook_instance = LarkWebHookService()
    result = lark_webhook_instance.create_service(data, user_request_data)
    return result


@app.put("/api/v1/webhook/", summary="Put Webhook Plan Plan", tags=["Webhook-Item"])
async def update_webhook_config(ReQuest: Request, request_data: UpdateWebhookItem):
    item_dict = request_data.dict()
    userRequestData = await ReQuest.json()
    lark_webhook_instance = LarkWebHookService()
    db_kube_config = lark_webhook_instance.query_service_id(item_dict.get('id'))
    if not (db_kube_config.get("data")):
        raise HTTPException(status_code=404, detail="Get Webhook not found")
    request_data = request_data.dict(exclude_unset=True)
    result = lark_webhook_instance.update_service(item_dict.get('id'), item_dict.get("business_name"),
                                                  item_dict.get("webhook_url"), item_dict.get("used"), userRequestData)
    return result


@app.delete("/api/v1/webhook", summary="Delete Webhook Plan", tags=["Webhook-Item"])
async def delete_webhook_config_v1(ReQuest: Request, request_data: DeleteWebhookItem):
    import asyncio
    item_dict = request_data.dict()
    userRequestData = await ReQuest.json()
    lark_webhook_instance = LarkWebHookService()
    db_webhook_config = lark_webhook_instance.query_service_id(item_dict.get('id'))
    if not (db_webhook_config.get("data")):
        raise HTTPException(status_code=404, detail="Get Webhook not found not delete")
    result = lark_webhook_instance.delete_service(item_dict.get("id"), userRequestData)
    return result


if __name__ == "__main__":
    logger = logging.getLogger("op-leak-api")
    logger.setLevel(logging.DEBUG)
    log_handler = TimedRotatingFileHandler(access_log_filename(), when="H", interval=1, backupCount=5, utc=False)
    logger.addHandler(log_handler)
    logger.info("fast-api logging start success")
    uvicorn.run(app, host="0.0.0.0", port=8888, log_level="debug")
