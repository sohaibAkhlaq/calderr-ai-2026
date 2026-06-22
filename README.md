# CalderR AI Internship 

Project location: Desktop/calderr-ai-2026

Author: Sohaib Akhlaq

Status: Week 0 Completed

Overview
This repository contains the Day 1 setup for the CalderR AI internship. It captures the local development environment, installed dependencies, and quick-start instructions to reproduce the environment.

Environment
- Python: 3.11.9
- Virtual environment: `calderr-env` (included, typically ignored by VCS)
- `pip` upgraded to the latest available version

Installed packages
- langchain
- langchain-groq
- langchain-community
- langgraph
- groq
- openai
- pydantic
- python-dotenv
- fastapi
- uvicorn
- chromadb
- sentence-transformers
- httpx
- rich
- typer
- pytest
- jupyter
- streamlit
- PyTorch 2.5.1

Version control
- Git configured
- SSH key generated for GitHub
- Repository: `calderr-ai-2026`

Containerization
- Docker Desktop installed
- `Dockerfile` included for building a project image

IDE
- Visual Studio Code with Python, Pylance and Jupyter extensions installed

Project structure
Desktop/calderr-ai-2026/
- `calderr-env/` — Virtual environment (should be ignored by Git)
- `.git/` — Git repository metadata
- `.gitignore` — Git ignore rules
- `.env.template` — Environment variable template
- `requirements.txt` — Python dependencies
- `main.py` — Main application entry point
- `test_setup.py` — Verification script for setup
- `Dockerfile` — Docker configuration
- `README.md` — This file

Quick start
1. Activate the virtual environment (PowerShell):

	.\calderr-env\Scripts\Activate.ps1

2. Run the application:

	python main.py

3. Build the Docker image:

	docker build -t calderr-ai-2026 .

4. Run the container:

	docker run --rm calderr-ai-2026

Notes
- The virtual environment directory is included locally for convenience; it should remain excluded from version control.
- Refer to `.env.template` for environment variables required by the application.

Acknowledgements
Day 1 setup completed and verified.

## Day 2 — Completed

- **Status:** Completed.
- **Feature added:** `dkeep` — a secure-state persistence helper for development workflows.

Notes:
- `dkeep` provides encrypted local storage for temporary keys and session data. It is intended for development use only; use a dedicated secret manager for production.

Security reminder:
- Never commit secrets to the repository. Keep local secrets in a `.env` file and ensure `.env` is listed in `.gitignore`.
- If `.env` was committed, stop tracking and remove it from history (instructions below).

How to stop tracking `.env` and remove it from Git history:

```bash
# Stop tracking the .env file and keep it locally
git rm --cached .env
git commit -m "Stop tracking .env and add to .gitignore"
git push origin main

# If secrets were committed earlier, remove them from history using BFG or git filter-repo
# Example (BFG):
#   bfg --delete-files .env
#   git reflog expire --expire=now --all && git gc --prune=now --aggressive
#   git push --force
```

Contact the repository maintainer for assistance with key rotation or history scrubbing.

See the detailed Day 2 summary: [day2-summary.txt](day2-summary.txt)
