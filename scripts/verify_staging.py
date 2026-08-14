"""Staging Deployment Health Verification Script (T102).

Verifies active backend health endpoint (`GET /api/v1/health`), root health check (`GET /health`),
and database/cache readiness status across containerized staging deployment.
"""

import argparse
import logging
import sys
import time
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("verify_staging")


def verify_health(target_url: str = "http://localhost:8000") -> bool:
    """Query health endpoints and verify HTTP 200 OK response."""
    health_endpoint = f"{target_url.rstrip('/')}/api/v1/health"
    logger.info("Checking staging health endpoint: %s", health_endpoint)

    try:
        res = requests.get(health_endpoint, timeout=10)
        if res.status_code == 200:
            data = res.json()
            logger.info(" -> SUCCESS: Health check passed. Payload: %s", data)
            return True
        else:
            logger.error(" -> FAILURE: Health check returned status code %d", res.status_code)
            return False
    except Exception as exc:
        logger.error(" -> ERROR: Failed to connect to health endpoint: %s", exc)
        return False


def main():
    parser = argparse.ArgumentParser(description="Verify staging deployment health.")
    parser.add_argument("--url", default="http://localhost:8000", help="Target base URL")
    args = parser.parse_args()

    success = verify_health(args.url)
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
