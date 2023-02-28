"""REST client handling, including SendGridStream base class."""

from __future__ import annotations

from pathlib import Path
from typing import Callable
from datetime import datetime

import requests
from singer_sdk.streams import RESTStream
from singer_sdk.tap_base import Tap

from singer_sdk.pagination import BaseOffsetPaginator, BaseAPIPaginator

from sendgrid import SendGridAPIClient
from python_http_client.client import Response

_Auth = Callable[[requests.PreparedRequest], requests.PreparedRequest]
SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")


class SendGridOffsetPaginator(BaseOffsetPaginator):
    def has_more(self, response: Response) -> bool:
        return len(response.to_dict) == self._page_size


class SendGridBasePaginator(BaseAPIPaginator):
    def __init__(self, page_size: int, start_value: int) -> None:
        super().__init__(start_value)
        self.page_size = page_size

    def has_more(self, response: Response) -> bool:
        return len(response.to_dict["messages"]) == self.page_size

    def _extract_dates(self, response: Response) -> list:
        return [
            datetime.strptime(message["last_event_time"], "%Y-%m-%dT%H:%M:%SZ")
            for message in response.to_dict["messages"]
        ]

    def get_next(self, response: Response) -> int:
        return max(self._extract_dates(response)).strftime("%Y-%m-%dT%H:%M:%SZ")

    def get_last(self, response: Response) -> int:
        return min(self._extract_dates(response)).strftime("%Y-%m-%dT%H:%M:%SZ")


class SendGridStream(RESTStream):
    """SendGrid stream class."""

    url_base = "https://api.sendgrid.com"
    headers = {"Accept": "application/json"}
    start_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    end_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

    def __init__(self, tap: Tap, paginator_type: str) -> None:
        super().__init__(tap)
        self.conn = SendGridAPIClient(api_key=self.config.get("api_key"))
        self.paginator_type = paginator_type
        self.page_size = self.config.get("batch_size", 500)
        self.paginator = self.get_new_paginator()

    def get_new_paginator(self):
        if self.paginator_type == "offset":
            return SendGridOffsetPaginator(start_value=0, page_size=500)
        elif self.paginator_type == "base":
            return SendGridBasePaginator(
                start_value=self.start_time, page_size=self.page_size
            )

    @property
    def get_unix_start_time(self):
        datetime_object = datetime.strptime(
            self.config["start_datetime"], "%Y-%m-%dT%H:%M:%SZ"
        )
        return int(datetime_object.timestamp())
