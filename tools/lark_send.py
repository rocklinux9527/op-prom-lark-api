from abc import ABC, abstractmethod

import requests

from tools.config import setup_logger


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
            message += f"开始时间：{alert_data.get('startsAt', '未知开始时间')}\n"

            if alert_data.get('status') == 'resolved':
                message += f"恢复时间：{alert_data.get('endsAt', '未知恢复时间')}\n"

            message += f"实例名称：{labels.get('instance', '未知实例')}\n"
            message += f"信息详情：{annotations.get('description', '无详细信息')}\n"
            message += f"解决方案：{generatorURL}\n"
            messages.append(message)
        return messages
        # # 取出 alerts 列表中的第一个 alert
        # alert_data = self.alert.get('alerts', [])[0]
        # labels = alert_data.get('labels', {})
        # generatorURL = alert_data.get('generatorURL', {})
        # annotations = alert_data.get('annotations', {})
        # message = f"**{labels.get('alertname', '未知告警')}**\n"
        # message += f"集群名称：{labels.get('prometheus', '未知集群')}\n"
        # message += f"告警名称：{labels.get('alertname', '未知告警')}\n"
        # message += f"命名空间：{labels.get('namespace', '未知命名空间')}\n"
        # message += f"告警状态：{alert_data.get('status', '未知状态')}\n"
        # message += f"告警级别：{labels.get('severity', '未知级别')}\n"
        # message += f"开始时间：{alert_data.get('startsAt', '未知开始时间')}\n"
        #
        # if alert_data.get('status') == 'resolved':
        #     message += f"恢复时间：{alert_data.get('endsAt', '未知恢复时间')}\n"
        #
        # message += f"实例名称：{labels.get('instance', '未知实例')}\n"
        # message += f"信息详情：{annotations.get('description', '无详细信息')}\n"
        # message += f"解决方案：{generatorURL}\n"
        # return message


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

# # 示例告警信息
# alert_data = {
#     "receiver": "default-receiver",
#     "status": "firing",
#     "alerts": [
#         {
#             "status": "firing",
#             "labels": {
#                 "alertname": "KubePodNotReady",
#                 "namespace": "default",
#                 "pod": "example-app-f4fddc88-ndtf6",
#                 "prometheus": "monitoring/prometheus-stack-kube-prom-prometheus",
#                 "severity": "warning",
#                 "container": "kube-state-metrics",
#                 "endpoint": "http",
#                 "instance": "10.244.36.80:8080",
#                 "job": "kube-state-metrics",
#                 "phase": "Pending",
#                 "service": "prometheus-stack-kube-state-metrics",
#                 "uid": "7b626232-5e22-4db9-8f6c-ba1fed705344"
#             },
#             "annotations": {
#                 "description": "Pod default/example-app-f4fddc88-ndtf6 has been in a non-ready state for longer than 15 minutes.",
#                 "summary": "Pod has been in a non-ready state for more than 15 minutes."
#             },
#             "startsAt": "2024-06-05T14:02:51.531Z",
#             "endsAt": "0001-01-01T00:00:00Z",
#             "generatorURL": "http://prometheus.k8s.local/graph?g0.expr=sum+by+%28namespace%2C+pod%2C+cluster%29+%28max+by+%28namespace%2C+pod%2C+cluster%29+%28kube_pod_status_phase%7Bjob%3D%22kube-state-metrics%22%2Cnamespace%3D~%22.%2A%22%2Cphase%3D~%22Pending%7CUnknown%7CFailed%22%7D%29+%2A+on+%28namespace%2C+pod%2C+cluster%29+group_left+%28owner_kind%29+topk+by+%28namespace%2C+pod%2C+cluster%29+%281%2C+max+by+%28namespace%2C+pod%2C+owner_kind%2C+cluster%29+%28kube_pod_owner%7Bowner_kind%21%3D%22Job%22%7D%29%29%29+%3E+0&g0.tab=1",
#             "fingerprint": "2dca31ec35b4c5d5"
#         }
#     ],
#     "groupLabels": {
#         "alertname": "KubePodNotReady"
#     },
#     "commonLabels": {
#         "alertname": "KubePodNotReady",
#         "namespace": "default",
#         "pod": "example-app-f4fddc88-ndtf6",
#         "prometheus": "monitoring/prometheus-stack-kube-prom-prometheus",
#         "severity": "warning",
#         "container": "kube-state-metrics",
#         "endpoint": "http",
#         "instance": "10.244.36.80:8080",
#         "job": "kube-state-metrics",
#         "phase": "Pending",
#         "service": "prometheus-stack-kube-state-metrics",
#         "uid": "7b626232-5e22-4db9-8f6c-ba1fed705344"
#     },
#     "commonAnnotations": {
#         "description": "Pod default/example-app-f4fddc88-ndtf6 has been in a non-ready state for longer than 15 minutes.",
#         "summary": "Pod has been in a non-ready state for more than 15 minutes."
#     },
#     "externalURL": "http://alertmanager.k8s.local",
#     "version": "4",
#     "groupKey": "{}:{alertname=\"KubePodNotReady\"}"
# }
