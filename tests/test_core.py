"""Tests standard tap features using the built-in SDK tests library."""

import datetime

from singer_sdk.testing import get_tap_test_class

from tap_sendgrid.tap import TapSendGrid


SAMPLE_CONFIG = {
    "start_date": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d"),
    "api_key": "test",
    # TODO: Initialize minimal tap config
}


# Run standard built-in tap tests from the SDK:
TestTapSendGrid = get_tap_test_class(
    tap_class=TapSendGrid,
    config=SAMPLE_CONFIG
)


# TODO: Create additional tests as appropriate for your tap.
