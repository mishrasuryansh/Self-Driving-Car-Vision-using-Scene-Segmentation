"""T041 Celery Worker Integration & Asynchronous Task Queue Verification Script.

Tests:
1. Verification of Celery app configuration (`celery_app`).
2. Registration of `tasks.process_segmentation_task` background worker task.
3. Synchronous test execution of `process_segmentation_task` in eager mode.
4. Validation of Section 8.2 metrics payload returned from worker task execution.
"""

import logging
import os
import sys

# Ensure repository root and backend directory are in sys.path
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
backend_path = os.path.join(repo_root, "backend")
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.core.celery_app import celery_app
from app.tasks.inference_tasks import process_segmentation_task

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_t041")


def test_celery_worker_task():
    print("[TEST 1] Testing Celery app instance configuration...")
    assert celery_app.main == "worker"
    print(f" -> Celery App Name: '{celery_app.main}'")
    print(f" -> Broker URL: '{celery_app.conf.broker_url}'")
    print(" -> PASSED! Celery configuration verified.")

    print("[TEST 2] Verifying task registration in Celery registry...")
    registered_tasks = celery_app.tasks
    assert "tasks.process_segmentation_task" in registered_tasks
    print(" -> Registered Task: 'tasks.process_segmentation_task'")
    print(" -> PASSED! Task registration verified.")

    print("[TEST 3] Executing process_segmentation_task in eager mode...")
    celery_app.conf.task_always_eager = True
    celery_app.conf.task_eager_propagates = True

    dummy_task_id = "test_task_uuid_12345"
    dummy_media_id = "test_media_uuid_67890"
    dummy_input_path = os.path.normpath("storage/uploads/test_input.jpg")

    # Ensure dummy input file directory exists
    os.makedirs(os.path.dirname(dummy_input_path), exist_ok=True)
    with open(dummy_input_path, "wb") as f:
        f.write(b"SYNTHETIC_TEST_INPUT_BYTES")

    task_result = process_segmentation_task.apply(
        args=[dummy_task_id, dummy_media_id, dummy_input_path, "image"],
        kwargs={"use_fp16": False, "use_torchscript": True},
    )

    res_data = task_result.get()
    assert res_data["task_id"] == dummy_task_id
    assert res_data["status"] == "completed"
    assert "metrics" in res_data
    metrics = res_data["metrics"]
    assert metrics["fps"] > 0
    assert metrics["avgInferenceMs"] > 0
    assert "classDistribution" in metrics
    assert os.path.exists(res_data["output_path"])

    print(f" -> Eager Task Execution Result: Status={res_data['status']}, Output={res_data['output_path']}")
    print(f" -> Performance Metrics: {metrics}")
    print(" -> PASSED! Celery task execution verified.")


def run_all():
    print("====================================================")
    print("RUNNING T041 CELERY WORKER INTEGRATION SUITE")
    print("====================================================")
    test_celery_worker_task()
    print("====================================================")
    print("ALL T041 VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("====================================================")


if __name__ == "__main__":
    run_all()
