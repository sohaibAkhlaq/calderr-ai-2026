# CalderR AI Internship — Day 1 Summary

Project location: Desktop/calderr-ai-2026

Author: Sohaib Akhlaq

Status: Day 1 complete — ready to proceed to Day 2

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
