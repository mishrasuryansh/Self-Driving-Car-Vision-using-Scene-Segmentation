"""Worker Process Entrypoint & Model Pre-loader (T051 & T052).

Initializes the Celery distributed worker application, pre-loads the DeepLabV3+ neural network weights
at startup into memory (T052), and exports the worker application instance.
"""

import logging
import os
import sys

# Ensure repository root and backend/worker directories are in sys.path
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
backend_path = os.path.join(repo_root, "backend")
engine_path = os.path.join(repo_root, "inference-engine")

if repo_root not in sys.path:
    sys.path.insert(0, repo_root)
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)
if engine_path not in sys.path:
    sys.path.insert(0, engine_path)

from app.config import settings
from app.core.celery_app import celery_app

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("worker.app.main")

# Pre-loaded model backend singleton instance (T052)
_model_instance = None


def get_preloaded_model():
    """Retrieve pre-loaded DeepLabV3+ model backend instance (T052)."""
    global _model_instance
    if _model_instance is None:
        try:
            from pipeline import DeepLabV3Backend
            logger.info("[T052] Pre-loading DeepLabV3+ model weights from '%s'...", settings.MODEL_WEIGHTS_PATH)
            _model_instance = DeepLabV3Backend(
                weights_path=settings.MODEL_WEIGHTS_PATH,
                device=settings.MODEL_DEVICE,
            )
            logger.info("[T052] Model pre-loaded successfully on device '%s'!", settings.MODEL_DEVICE)
        except Exception as exc:
            logger.warning("[T052] Pre-loading model failed (%s). Worker will operate in lazy/fallback mode.", exc)
    return _model_instance


# Trigger pre-loading on module import (T052)
get_preloaded_model()

app = celery_app

__all__ = ["app", "celery_app", "get_preloaded_model"]
