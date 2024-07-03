# op-prometheus-webhook-lark-api
```
 promethus alertManger 扩展webhook lark api 
```

1.1 传统方式部署
```
  1.部署mysql数据库服务;
  2.安装python 3.7 （参考:https://www.python.org/downloads/） 下载并安装
  3.执行pip -r install requirements.txt 
  4.启动服务:
  $ python3.7 main.py
```

1.2 容器化方式部署
```
   1.自行安装docker-compose 基础环境
   2.运行 install_dir/install_shell.sh 部署脚本等待完成部署
   3.部署成功出现如下提示-部署成功.
   部署完毕,访问机器http://localhost:8888  Success

```
1.3 告警显示
![告警模版实例](https://github.com/rocklinux9527/op-prom-lark-api/assets/120091528/c481c3ad-fc24-4f41-b151-ea6801325749)

1.4 发送测试接口数据
```
curl --location --request POST 'http://127.0.0.1:8888/api/v1/all-lark-webhooks?group=default' \
--header 'Content-Type: application/json' \
--data-raw '{
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
}'
```
