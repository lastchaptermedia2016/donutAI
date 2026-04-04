"""Sentry configuration for backend error tracking."""

import os
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.logging import LoggingIntegration


def init_sentry():
    """Initialize Sentry for error tracking."""
    sentry_dsn = os.getenv("SENTRY_DSN")
    environment = os.getenv("ENVIRONMENT", "development")
    release = os.getenv("APP_VERSION", "0.1.0")
    
    if not sentry_dsn:
        print("Sentry DSN not configured, skipping Sentry initialization")
        return
    
    sentry_sdk.init(
        dsn=sentry_dsn,
        environment=environment,
        release=release,
        integrations=[
            FastApiIntegration(),
            LoggingIntegration(
                level=logging.INFO,
                event_level=logging.ERROR,
            ),
        ],
        traces_sample_rate=0.1,  # Capture 10% of transactions
        send_default_pii=False,  # Don't send personal data
        max_breadcrumbs=50,
        attach_stacktrace=True,
    )
    
    print(f"Sentry initialized for {environment} environment")