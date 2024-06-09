# 日志配置
import sys
import os
from datetime import datetime
import logging
from logging.handlers import TimedRotatingFileHandler


# LarkWebhookHeader 配置前端显示表头
LarkWebhookHeader = [
    {"name": "id", "alias": "唯一标识"},
    {"name": "business_name", "alias": "业务名称"},
    {"name": "webhook_url", "alias": "Webhook地址"},
    {"name": "used", "alias": "用途"},
    {"name": "create_time", "alias": "创建时间"}
]

LarkAlarmHeader = [
    {"name": "id", "alias": "唯一标识"},
    {"name": "receiver", "alias": "接收器名称"},
    {"name": "status", "alias": "状态"},
    {"name": "alerts", "alias": "告警内容"},
    {"name": "groupLabels", "alias": "组标签"},
    {"name": "commonLabels", "alias": "通用标签"},
    {"name": "commonAnnotations", "alias": "通用注解"},
    {"name": "externalURL", "alias": "解决URL"},
    {"name": "create_time", "alias": "创建时间"}
]


def access_log_filename():
    """
    1.日志输出文件格式设置
    Returns:

    """
    root_dir = os.path.dirname(os.path.abspath(__file__))
    log_dir = os.path.join(root_dir, "logs")
    if "tools" in log_dir:
        log_dir = log_dir.replace("/tools", "")
    formatted_time = (datetime.now().strftime("%Y%m%d%H"))  # cst 时间
    return os.path.join(log_dir, f"op-lark-api.log")

def setup_logger():
    """
    初始化日志记录器
    """
    logger = logging.getLogger("op-prom-lark-api")
    logger.setLevel(logging.DEBUG)
    log_handler = TimedRotatingFileHandler(access_log_filename(), when="H", interval=1, backupCount=5, utc=False)
    logger.addHandler(log_handler)
    return logger
