"""Stream type classes for tap-sendgrid."""

from __future__ import annotations

from typing import Iterable, Optional

from singer_sdk import typing as th  # JSON Schema typing helpers

from tap_sendgrid.client import SendGridStream
import logging

LOGGER = logging.getLogger(__name__)


class BouncesStream(SendGridStream):
    """Define custom stream."""

    name = "bounces"
    path = "/suppression/bounces"
    primary_keys = ["email"]
    replication_key = "created"
    schema = th.PropertiesList(
        th.Property("email", th.StringType),
        th.Property("created", th.IntegerType),
        th.Property("reason", th.StringType),
        th.Property("status", th.StringType),
        th.Property("error", th.StringType),
    ).to_dict()

    def get_records(self, context: dict | None) -> Iterable[dict]:
        """Return a generator of row-type dictionary objects.

        Each row emitted should be a dictionary of property names to their values.
        """

        page_size = self.page_size
        offset = 0
        if context is not None:
            start_time = self.get_starting_replication_key_value(context)
        else:
            start_time = self.get_unix_start_time

        while True:
            resp = self.conn.client.suppression.bounces.get(
                request_headers=self.headers,
                query_params={
                    "start_time": start_time,
                    "offset": offset,
                    "limit": page_size,
                },
            )

            yield from resp.to_dict

            if not self.paginator.has_more(resp):
                break

            offset = self.paginator.get_next(resp)


class EmailActivitySteam(SendGridStream):
    name = "email_activity"
    path = "/v3/messages"
    primary_keys = ["email"]
    replication_key = "last_event_time"
    schema = th.PropertiesList(
        th.Property("from_email", th.StringType),
        th.Property("msg_id", th.StringType),
        th.Property("subject", th.StringType),
        th.Property("to_email", th.StringType),
        th.Property("status", th.StringType),
        th.Property("opens_count", th.IntegerType),
        th.Property("clicks_count", th.IntegerType),
        th.Property("last_event_time", th.DateTimeType),
    ).to_dict()

    def get_records(self, context: dict | None) -> Iterable[dict]:
        """Return a generator of row-type dictionary objects.

        Each row emitted should be a dictionary of property names to their values.
        """
        page_size = self.page_size
        from_email = self.config.get("from_email")
        if context is not None:
            start_time = context.get("last_datetime")
            start_time = self.get_starting_replication_key_value(context)
        else:
            start_time = self.config.get("start_datetime")
        end_time = self.end_time

        while True:
            query = (
                f'from_email="{from_email}" '
                f'AND last_event_time BETWEEN TIMESTAMP "{start_time}" '
                f'AND TIMESTAMP "{end_time}"'
            )

            resp = self.conn.client.messages.get(
                request_headers=self.headers,
                query_params={"query": query, "limit": page_size},
            )

            yield from resp.to_dict["messages"]

            if not self.paginator.has_more(resp):
                break

            end_time = self.paginator.get_last(resp)
