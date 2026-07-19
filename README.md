# Phoenix AI X

Phoenix AI X is a production-ready foundation for an autonomous AI quantitative research platform. It is designed to grow from exploratory research into a governed, observable platform for strategy discovery, model training, portfolio research, backtesting, paper trading, and—only after explicit governance—live execution.

> **Current scope:** repository scaffolding only. No trading logic, order routing, data collection, or live execution is implemented.

## Architecture

Phoenix AI X follows Clean Architecture. Dependencies point inward; the domain remains independent of FastAPI, Streamlit, SQLAlchemy, exchanges, and ML frameworks.

```text
Presentation (API / Dashboard / CLI)
              ↓
Application (use cases, commands, queries)
              ↓
Domain (entities, policies, ports)
              ↑
Infrastructure (database, cache, events, external adapters)

Research (experiments, models, training) integrates through application ports.
```

The composition root in `bootstrap.py` provides explicit dependency injection. Repository, Factory, Strategy, and Observer patterns have dedicated homes, ready to be introduced as capabilities are implemented.

## Features planned

- Multi-agent AI research and durable knowledge management
- Feature discovery, strategy generation, and experiment tracking
- PyTorch, TensorFlow, gradient boosting, RL, and hyperparameter optimization
- Distributed Ray/Dask research workloads and GPU/TPU-ready execution
- Institutional-quality backtesting, risk, portfolio optimization, and analytics
- Paper and live trading adapters, introduced behind guarded execution boundaries
- MLflow and optional Weights & Biases experiment tracking

## Installation

```bash
git clone <your-repository-url>
cd Phoenix-AI-X
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pre-commit install
cp .env.example .env
```

For the lean API scaffold, install the package directly with `pip install -e .`. Heavy ML and distributed dependencies are declared in the requirements file and can be made optional as deployment profiles mature.

## Quick start

```bash
pytest
uvicorn phoenix_ai.api.main:app --reload
streamlit run src/phoenix_ai/dashboard/app.py
```

The health check is available at `http://localhost:8000/health`. For local platform dependencies, start `docker compose up postgres redis`; add the API and dashboard with `--profile platform`.

## Directory structure

```text
src/phoenix_ai/
├── domain/          # Pure business entities and ports
├── application/     # Use cases and orchestration
├── infrastructure/  # Persistence, cache, events, external adapters
├── presentation/    # Presentation contracts
├── research/        # Research lifecycle and hypotheses
├── experiments/     # Experiment tracking abstractions
├── models/ training/ optimization/ features/
├── strategy/ backtesting/ execution/ portfolio/ risk/
├── ai/ agents/ kernel/ memory/ knowledge/
├── market/ analytics/ database/ events/ config/ utils/
└── api/ dashboard/ cli/  # Delivery mechanisms
docs/                # Architecture, API, deployment, research, experiments
tests/               # Unit, integration, performance, regression
notebooks/           # Colab-ready learning and research notebooks
datasets/ models/ reports/  # Git-ignored operational assets
```

## Tech stack

Python 3.12+, FastAPI, Streamlit, SQLAlchemy, SQLite/PostgreSQL, Redis, PyTorch, TensorFlow, XGBoost, LightGBM, CatBoost, scikit-learn, Ray, Dask, Optuna, MLflow, Plotly, CCXT, Docker, and GitHub Actions.

## Roadmap and future plans

See [ROADMAP.md](ROADMAP.md) for milestone sequencing. Future releases will add data governance, reproducible research environments, model and feature registries, distributed experiment scheduling, robust simulator/backtesting policies, and controlled execution integrations.

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md), follow the [Code of Conduct](CODE_OF_CONDUCT.md), and report vulnerabilities using [SECURITY.md](SECURITY.md). All contributions must preserve layer boundaries, type hints, tests, and automated quality checks.

## License

Licensed under the MIT License. See [LICENSE](LICENSE).
