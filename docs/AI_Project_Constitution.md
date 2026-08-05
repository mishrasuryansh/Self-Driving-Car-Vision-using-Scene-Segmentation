# AI Project Constitution

## Project

**Self-Driving Car Vision using Scene Segmentation**

This document defines the permanent engineering rules for every AI coding agent working on this repository.

The Project Master Documentation and Implementation Roadmap are the SINGLE SOURCE OF TRUTH.

---

# Architecture Rules

Never redesign the architecture.

Never rename folders.

Never move files.

Never delete working code.

Never introduce frameworks not already approved.

Never change APIs unless explicitly instructed.

Always preserve backward compatibility.

---

# Folder Rules

The project structure is fixed.

New files must be created only inside the appropriate module.

Never create duplicate modules.

Never place business logic inside API routes.

Never mix frontend and backend logic.

---

# Coding Standards

Always use

- Clean Architecture
- SOLID Principles
- Type Hints
- Structured Logging
- Typed Exceptions
- Small Functions
- One Responsibility Per Class

Never use

- print()
- bare except
- magic numbers
- hardcoded secrets
- duplicated logic

---

# Documentation Rules

Whenever required

Update

- README
- API Documentation
- Architecture Diagram
- Deployment Notes

Never leave outdated documentation.

---

# Testing Rules

Every feature should be testable.

When appropriate

Write

- Unit Tests
- Integration Tests
- Manual Test Instructions

Never break existing functionality.

---

# Git Rules

One task = One commit.

Commit messages should follow

feat(T001): initialize repository

feat(T002): configure tooling

fix(T013): correct taxonomy mapping

docs(T001): update README

---

# Human Checkpoints

The AI must NEVER perform

- Dataset registration
- Dataset licensing
- External authentication
- Cloud account creation
- GPU training execution
- Production deployment

The AI should generate

- Code
- Configurations
- Documentation
- Verification scripts

Human approval is required before continuing after these checkpoints.

---

# AI Agent Behavior

Implement ONLY the requested task.

Never implement future tasks.

Never modify unrelated files.

Never guess missing requirements.

If information is missing

STOP

Explain what is missing.

Wait for confirmation.

---

# Definition of Done

A task is complete only if

- Acceptance Criteria satisfied
- Exit Criteria satisfied
- Code compiles
- Tests pass (if applicable)
- Logging implemented
- Error handling implemented
- Type hints added
- Documentation updated
- Ready for Git commit

---

# Repository Context

Always inspect the current repository before making changes.

The repository state is more important than assumptions.

If the repository differs from the prompt

Use the repository as the source of truth

unless explicitly instructed otherwise.

---

# Final Rule

The objective is to build a production-quality AI web application suitable for

- Final Year Major Project
- GitHub Portfolio
- Resume
- AI/ML Showcase
- Campus Placement
- Deployment

Never optimize for shortcuts.

Always optimize for maintainability, readability, scalability, and correctness.
