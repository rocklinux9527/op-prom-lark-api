from abc import ABC, abstractmethod

import requests
from datetime import datetime, timedelta
from tools.config import setup_logger
from tools.prom_data_time import add_hours_to_iso8601

# 定义抽象基类
class AlertTemplate(ABC):
    """
    AlertTemplate 类是一个抽象基类，用于定义告警消息发送的通用步骤。
    子类需要实现 get_title_info 方法来提供特定的标题和颜色信息。
    """
    def __init__(self, alert):
        self.alert = alert

    def send_message(self, webhook_url):
        """
        发送告警消息到指定的 webhook URL。
        """
        title_color, title = self.get_title_info()
        messages = self.create_messages()
        logger = setup_logger()
        results = []
        if len(messages) == 1:
            message = messages[0]
            data = self.build_payload(title_color, title, message)
            result = self.post_message(webhook_url, data, logger)
            results.append(result)
        else:
            for message in messages:
                data = self.build_payload(title_color, title, message)
                result = self.post_message(webhook_url, data, logger)
                results.append(result)
        return results

    def build_payload(self, title_color, title, message):
        """
        构建消息的请求数据。
        :param title_color: 消息标题颜色。
        :param title: 消息标题。
        :param message: 消息内容。
        :return: 构建好的请求数据。
        """
        return {
            "msg_type": "interactive",
            "card": {
                "config": {
                    "wide_screen_mode": True
                },
                "elements": [
                    {
                        "tag": "markdown",
                        "content": message.strip()
                    }
                ],
                "header": {
                    "template": title_color,
                    "title": {
                        "tag": "plain_text",
                        "content": title
                    }
                }
            }
        }

    def post_message(self, webhook_url, data, logger):
        """
        发送请求并记录日志。
        :param webhook_url: Webhook URL，用于发送告警消息。
        :param data: 请求数据。
        :param logger: 日志记录器。
        """
        try:
            response = requests.post(webhook_url, json=data)
            # logger.info(f"Request payload: {data}")
            # logger.info(f"Response text: {response.text}")
            if response.status_code == 200 and response.json().get("StatusCode") == 0:
                logger.info("消息发送成功")
                return {"code": 20000, "data": response.text, "messages": "send leak success", "status": True}
            else:
                logger.error(f"消息发送失败: {response.status_code}, {response.text}")
                return {"code": 50000, "data": response.text, "messages": "send leak fail", "status": False}
        except Exception as e:
            logger.error(f"消息发送失败: {str(e)}")
            return {"code": 50000, "data": str(e), "messages": "send leak fail", "status": False}

    @abstractmethod
    def get_title_info(self):
        """
        抽象方法，获取标题颜色和标题内容。
        子类必须实现此方法。
        """
        pass

    def create_messages(self):
        """
        创建告警消息内容。
        """
        messages = []
        for alert_data in self.alert.get('alerts', []):
            labels = alert_data.get('labels', {})
            generatorURL = alert_data.get('generatorURL', {})
            annotations = alert_data.get('annotations', {})
            message = f"**{labels.get('alertname', '未知告警')}**\n"
            message += f"集群名称：{labels.get('prometheus', '未知集群')}\n"
            message += f"告警名称：{labels.get('alertname', '未知告警')}\n"
            message += f"命名空间：{labels.get('namespace', '未知命名空间')}\n"
            message += f"告警状态：{alert_data.get('status', '未知状态')}\n"
            message += f"告警级别：{labels.get('severity', '未知级别')}\n"

            start_time = alert_data.get('startsAt', '未知开始时间')
            if start_time != '未知开始时间':
               start_time = add_hours_to_iso8601(start_time, 8)
            message += f"开始时间：{start_time }\n"
            if alert_data.get('status') == 'resolved':
                end_time = alert_data.get('endsAt', '未知恢复时间')
                if end_time != '未知恢复时间':
                   end_time = add_hours_to_iso8601(end_time, 8)
                   message += f"恢复时间: {end_time} \n"
                else:
                   message += "恢复时间：未知恢复时间\n"
            message += f"实例名称：{labels.get('instance', '未知实例')}\n"
            message += f"信息详情：{annotations.get('description', '无详细信息')}\n"
            solution  = annotations.get('solution', '无解决方案-请SRE补充')
            generatorurl = "点击我查看"
            message += f"解决方案: [{generatorurl}]({solution})\n"
            message += f"触发条件：[{generatorurl}]({generatorURL})\n"
            messages.append(message)
        return messages

class FiringAlertTemplate(AlertTemplate):
    """
    FiringAlertTemplate 类是 AlertTemplate 的具体实现类。
    用于生成告警状态为 "firing" 的告警信息
    """

    def get_title_info(self):
        return 'red', "Prometheus告警信息"


class ResolvedAlertTemplate(AlertTemplate):
    """
    ResolvedAlertTemplate 类是 AlertTemplate 的具体实现类。
    用于生成告警状态为 "resolved" 的告警信息。
    """
    def get_title_info(self):
        return 'green', "Prometheus恢复信息"


class UnknownAlertTemplate(AlertTemplate):
    """
    UnknownAlertTemplate 类是 AlertTemplate 的具体实现类。
    用于生成未知状态的告警信息。
    """
    def get_title_info(self):
        return 'yellow', "Prometheus未知状态"


def send_lark_alert(alert_info, webhook_url):
    """
    发送 Lark 告警信息。
    """
    if not alert_info:
        return {"code": 50000, "data": "", "messages": "fun alert_info is empty", "status": False}
    if not webhook_url:
        return {"code": 50000, "data": "", "messages": "fun webhook_url is empty", "status": False}
    # 根据告警状态选择合适的模板类
    if alert_info['status'] == 'firing':
        alert_template = FiringAlertTemplate(alert_info)
    elif alert_info['status'] == 'resolved':
        alert_template = ResolvedAlertTemplate(alert_info)
    else:
        alert_template = UnknownAlertTemplate(alert_info)
    return alert_template.send_message(webhook_url)
