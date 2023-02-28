"""SendGrid tap class."""

from __future__ import annotations

from singer_sdk import Tap
from singer_sdk import typing as th  # JSON schema typing helpers

# TODO: Import your custom stream types here:
from tap_sendgrid.streams import BouncesStream, SendGridStream, EmailActivitySteam


class TapSendGrid(Tap):
    """SendGrid tap class."""

    name = "tap-sendgrid"

    # TODO: Update this section with the actual config values you expect:
    config_jsonschema = th.PropertiesList(
        th.Property(
            "api_key",
            th.StringType,
            required=True,
            secret=True,  # Flag config as protected.
            description="The token to authenticate against the API service",
        ),
        th.Property(
            "start_datetime",
            th.DateTimeType,
            description="The earliest record date to sync",
        ),
        th.Property(
            "from_email",
            th.StringType,
            description="The email address that was used as sender",
        ),
    ).to_dict()

    def discover_streams(self) -> list[SendGridStream]:
        """Return a list of discovered streams.

        Returns:
            A list of discovered streams.
        """
        return [
            BouncesStream(self, paginator_type="offset"),
            EmailActivitySteam(self, paginator_type="base"),
        ]


if __name__ == "__main__":
    TapSendGrid.cli()
