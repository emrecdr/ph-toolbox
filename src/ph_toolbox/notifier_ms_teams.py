import json
from datetime import datetime
from typing import List, Optional

import requests

from .config import config


def notify_ms_teams_info(message: str, header: str = "", extras: Optional[List[str]] = None):
    return notify_ms_teams(message, header, extras, "general")


def notify_ms_teams_error(message: str, header: str = "", extras: Optional[List[str]] = None):
    return notify_ms_teams(message, header, extras, "error")


def notify_ms_teams_fatal_error(message: str, header: str = "", extras: Optional[List[str]] = None):
    return notify_ms_teams(message, header, extras, "fatal_error")


def notify_ms_teams(message: str, header: str = "", extras: Optional[List[str]] = None, level="general"):
    ms_teams_webhook_url = config(f"ms_teams_webhook_url_{level}")

    dt = datetime.now()

    body = [
        {"type": "TextBlock", "text": header, "size": "Medium", "weight": "Bolder", "wrap": True, "style": "heading"},
        {"type": "TextBlock", "text": message, "wrap": True, "spacing": "Medium", "separator": True},
        {
            "type": "TextBlock",
            "text": f"Created {dt.isoformat(' ')}",
            "wrap": True,
            "separator": True,
            "size": "Small",
            "spacing": "Medium",
            "horizontalAlignment": "Right",
            "isSubtle": True,
            "weight": "Lighter",
        },
    ]

    body_extras = (
        [
            {"type": "TextBlock", "text": extra, "wrap": True, "spacing": "Small", "weight": "Lighter"}
            for extra in extras
            if extra != "" and extra is not None
        ]
        if extras is not None
        else []
    )

    payload = {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "contentUrl": None,
                "content": {
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "type": "AdaptiveCard",
                    "version": "1.5",
                    "body": body[:-1] + body_extras + body[-1:],
                },
            }
        ],
    }

    headers = {"Content-Type": "application/json"}
    response = requests.post(ms_teams_webhook_url, headers=headers, data=json.dumps(payload))
    return response.text.encode("utf8")
