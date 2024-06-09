from fastapi import FastAPI, Request, HTTPException, Body
from pydantic import BaseModel, ValidationError, validator, HttpUrl
from typing import List, Dict, Any

class CreateWebhookItem(BaseModel):
    business_name: str
    webhook_url: str
    used: str

class UpdateWebhookItem(BaseModel):
    id: int
    business_name: str
    webhook_url: str
    used: str

class DeleteWebhookItem(BaseModel):
    id: int


class AlertItem(BaseModel):
    status: str
    labels: Dict[str, str]
    annotations: Dict[str, str]
    startsAt: str
    endsAt: str
    generatorURL: HttpUrl
    fingerprint: str

class SendLarkWebhook(BaseModel):
    receiver: str
    status: str
    alerts: List[AlertItem]
    groupLabels: Dict[str, str]
    commonLabels: Dict[str, str]
    commonAnnotations: Dict[str, str]
    externalURL: HttpUrl
    version: str
    groupKey: str
    truncatedAlerts: int

    class Config:
        arbitrary_types_allowed = True
