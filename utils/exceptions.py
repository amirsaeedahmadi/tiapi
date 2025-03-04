import logging
import os
import sys
import traceback

import sentry_sdk

logger = logging.getLogger(__name__)


def report_exception():
    if os.environ.get("DJANGO_SETTINGS_MODULE") == "config.settings.production":
        sentry_sdk.capture_exception()
    else:
        traceback.print_exception(*sys.exc_info())
