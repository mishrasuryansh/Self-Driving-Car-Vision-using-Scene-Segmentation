# Self-Driving Car Vision using Scene Segmentation

[![PR Pipeline](https://github.com/mishrasuryansh/Self-Driving-Car-Vision-using-Scene-Segmentation/actions/workflows/pr-pipeline.yml/badge.svg)](https://github.com/mishrasuryansh/Self-Driving-Car-Vision-using-Scene-Segmentation/actions)

A web-based AI platform for real-time and asynchronous pixel-level semantic scene segmentation of road images and videos, enabling autonomous vehicle perception analysis with interactive visual overlays and performance metrics.

## Getting Started

Follow these instructions to set up and run the local development environment using Docker Compose.

### Prerequisites

- [Git](https://git-scm.com/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (with Docker Compose v2.0+)
- [Python 3.11+](https://www.python.org/) (for pre-commit hooks and local script tools)

### Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/mishrasuryansh/Self-Driving-Car-Vision-using-Scene-Segmentation.git
   cd Self-Driving-Car-Vision-using-Scene-Segmentation
   ```

2. **Create environment file**:
   Copy the example environment template to `.env`:
   ```bash
   cp .env.example .env
   ```

3. **Start container services**:
   Launch all microservices (frontend, backend, worker, inference engine, MongoDB, and Redis):
   ```bash
   docker compose -f infra/docker-compose.yml up --build -d
   ```

4. **Access service endpoints**:
   Once started, the services are available at the following URLs:
   - **Frontend Web UI**: [http://localhost:3000](http://localhost:3000)
   - **Backend FastAPI Service**: [http://localhost:8000](http://localhost:8000)
   - **MongoDB Database**: `localhost:27017`
   - **Redis Cache & Broker**: `localhost:6379`

   *(Note: Default ports can be customized by modifying port variables in your `.env` file).*

5. **Stop container services**:
   To stop and remove running containers:
   ```bash
   docker compose -f infra/docker-compose.yml down
   ```

## Contributing & Developer Setup

### Code Formatting & Quality
This repository uses `.editorconfig` for consistent formatting across editors and `pre-commit` hooks for automatic quality checks.

#### Pre-Commit Setup
To set up pre-commit hooks locally:

1. Install `pre-commit`:
   ```bash
   pip install pre-commit
   ```
2. Install the git hook scripts:
   ```bash
   pre-commit install
   ```
3. Run pre-commit checks manually on all files:
   ```bash
   pre-commit run --all-files
   ```

### License
This project is licensed under the [MIT License](LICENSE).
