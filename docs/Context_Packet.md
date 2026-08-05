====================================================
CONTEXT PACKET
====================================================
PROJECT NAME: Self-Driving Car Vision using Scene Segmentation
PROJECT GOAL: A web-based AI platform where a user uploads a road-scene
image or video and receives an accurate, pixel-level semantic segmentation
overlay (road, vehicle, pedestrian, sky, building, vegetation), with
history and analytics — replacing the current CLI-only proof of concept.

CURRENT ARCHITECTURE: Three-tier system — React frontend → FastAPI
backend → Inference Engine, with a Redis-backed job queue + Worker for
async video processing, a database (users/jobs/models), and file/object
storage for media artifacts. Each tier is independently containerized
and independently scalable.

FOLDER STRUCTURE (fixed — never rename/move):
frontend/ · backend/app/{api,core,models,schemas,services} ·
inference-engine/{models,pipeline,weights} · worker/app/tasks ·
storage/{uploads,outputs} · infra/{docker,ci-cd} · docs/ · scripts/

TECHNOLOGY STACK: Python (FastAPI backend, PyTorch/torchvision inference
engine, Celery/RQ worker), React frontend, Redis (broker), MongoDB
(primary DB, per Section 9), Docker + Docker Compose, GitHub Actions CI.

CODING STANDARDS: Clean Architecture, SOLID, type hints everywhere,
structured logging (never print()), typed exceptions (never bare
except), no magic numbers, small functions, one responsibility per
class, existing naming conventions preserved.

PROJECT CONSTITUTION:
- Project Master Documentation and Implementation Roadmap are the
  SINGLE SOURCE OF TRUTH. Never violate them.
- Never redesign architecture, rename folders, move files, modify
  unrelated modules, or change APIs unless explicitly instructed.
- Never remove working code. Never introduce new frameworks.
- Always: Clean Architecture, SOLID, production-quality code, backward
  compatibility, logging, exception handling, type hints, docs updated
  when required.
- If a task conflicts with the architecture: STOP, explain the
  conflict, wait for confirmation. Never guess.

CURRENT MILESTONE: [fill in — e.g., M1: Project Foundation]
CURRENT EPIC: [fill in — e.g., EP1: Project Foundation]
CURRENT FEATURE: [fill in — e.g., F1.1: Monorepo Scaffold]
COMPLETED TASKS: [fill in — e.g., T001–T008 complete]
CURRENT BRANCH: One feature branch per Epic — feature/EP{n}-{slug};
  task commits land on the active epic branch, merged to main at the
  epic's milestone boundary.

KNOWN TECHNICAL DEBT (from Master Doc Section 2.4, being retired task
by task — do not reintroduce): deprecated pretrained=True API; placeholder
VOC→driving-class simulation; per-run model reload; missing image-input
path; missing utils/ modules; no input validation; no tests.

CURRENT CONSTRAINTS: No dedicated GPU cluster (Section 4.8) — design for
GPU-optional/CPU-fallback. Single-semester academic timeline. Any task
involving GPU training, external dataset licensing, irreversible
architectural decisions, or cloud deployment requires human execution —
the AI agent generates code/config/docs only, never executes these.
====================================================
