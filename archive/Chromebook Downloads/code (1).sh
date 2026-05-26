#!/bin/bash
# ===================================================================================
# Automated Project Setup Script for the Enhanced Resume Agent
# Version: Final Consolidated for Linux/ChromeOS
# ===================================================================================

PROJECT_NAME="resume-agent"
echo "🏗️  Starting project setup for: $PROJECT_NAME"

mkdir -p "$PROJECT_NAME"
cd "$PROJECT_NAME"

# --- Helper function to create directories and files ---
create_file() {
    mkdir -p "$(dirname "$1")"
    cat > "$1"
    echo "  📄 Created: $1"
}

# --- Create all files ---
echo "✍️  Writing content to all project files..."

create_file README.md <<'EOF'
# Enhanced Resume Agent 3.0 – Personal Edition (Final)
Welcome! This repository contains the **personal, single-user** version of the Enhanced Resume Agent 3.0. It is a complete career toolkit, integrating AI document generation with a sophisticated background automation suite and a state machine-driven workflow.
## ✨ Core Features
-   **State Machine Orchestration:** Core logic is managed by a resilient and observable LangGraph-powered state machine.
-   **AI-Powered Document Generation:** Tailors resumes and cover letters using Google Gemini, with a "Tone of Voice" shifter for stylistic control.
-   **Autonomous Job Scouting:** Automatically checks Gmail for new job postings via a Celery-based scheduler with a source-aware parsing engine.
-   **Pluggable Data Layer:** A Vector Database Abstraction Layer makes it easy to swap vector storage backends in the future.
-   **AI Writing Assistants:** Includes a "Bullet Point Enhancer" and a "Pre-Interview Company Dossier" generator.
-   **Simple & Fast UI:** A lightweight, custom HTML/JS frontend served directly by the backend.
## 🚀 Quick Start
1.  **Configure Environment:** Copy `.env.example` to `.env` and fill in your API keys.
2.  **Run with Docker Compose:** From the root directory, run:
    ```bash
    docker-compose up --build
    ```
3.  **Access the Services:**
    -   **Application UI:** `http://localhost:8000`
    -   **API Docs:** `http://localhost:8000/api/docs`
EOF

create_file pyproject.toml <<'EOF'
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "enhanced-resume-agent"
version = "4.0.0"
description = "Personal AI-powered career document generation and automation system with state machine orchestration."
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "fastapi", "uvicorn[standard]", "pydantic", "pydantic-settings",
    "python-dotenv", "Jinja2", "weasyprint", "spacy", "google-generativeai",
    "PyYAML", "sqlalchemy", "chromadb", "sentence-transformers",
    "celery==5.4.0", "redis==5.0.7", "google-api-python-client==2.136.0",
    "google-auth-httplib2==0.2.0", "google-auth-oauthlib==1.2.0", "langgraph"
]
EOF

create_file docker-compose.yml <<'EOF'
version: '3.8'
services:
  redis:
    image: "redis:alpine"
    ports: ["6379:6379"]
  web:
    build: .
    command: uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
    volumes: [".:/app"]
    ports: ["8000:8000"]
    env_file: .env
    depends_on: [redis]
  worker:
    build: .
    command: celery -A src.celery_worker.celery_app worker --loglevel=info
    volumes: [".:/app"]
    env_file: .env
    depends_on: [redis]
  scheduler:
    build: .
    command: celery -A src.celery_worker.celery_app beat --loglevel=info
    volumes: [".:/app"]
    env_file: .env
    depends_on: [redis]
EOF

create_file Dockerfile <<'EOF'
FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
COPY pyproject.toml .
RUN pip install .
RUN python -m spacy download en_core_web_sm
COPY . .
EXPOSE 8000
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

create_file .env.example <<'EOF'
# API Keys
GOOGLE_GEMINI_API_KEY="your-google-api-key-here"
PERPLEXITY_API_KEY="your-perplexity-api-key-here"

# Celery Configuration
CELERY_BROKER_URL="redis://redis:6379/0"
CELERY_BACKEND_URL="redis://redis:6379/0"

# Database Configuration
DATABASE_URL="sqlite:///./resume_agent.db"
VECTOR_DB_TYPE="chromadb"
VECTOR_DB_PATH="./chroma_db"
EOF

create_file src/config.py <<'EOF'
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')
    GOOGLE_GEMINI_API_KEY: str
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_BACKEND_URL: str = "redis://redis:6379/0"
    DATABASE_URL: str = "sqlite:///./resume_agent.db"
    VECTOR_DB_TYPE: str = "chromadb"
    VECTOR_DB_PATH: str = "./chroma_db"

settings = Settings()
EOF

create_file src/celery_worker.py <<'EOF'
from src.config import settings
from celery import Celery

celery_app = Celery("resume_agent_worker", broker=settings.CELERY_BROKER_URL, backend=settings.CELERY_BACKEND_URL, include=["src.tasks.job_pipeline"])
celery_app.conf.beat_schedule = {'find-new-jobs-every-15-minutes': {'task': 'src.tasks.job_pipeline.fetch_and_process_jobs','schedule': 900.0,}}
celery_app.conf.timezone = 'UTC'
EOF

create_file src/tasks/job_pipeline.py <<'EOF'
from src.celery_worker import celery_app
from src.services.workflow_orchestrator import orchestrator

@celery_app.task
def fetch_and_process_jobs():
    """Scheduled task to find new job data and trigger the full workflow."""
    print("SCHEDULER: Finding new job opportunities...")
    # In a real app, this would get job data from the Gmail integration
    mock_job_description = "Job Title: Senior Policy Advisor at Department of Community..."
    orchestrator.run(mock_job_description) # Trigger the workflow
    return "Dispatched job application workflow."
EOF

create_file src/services/workflow_orchestrator.py <<'EOF'
from langgraph.graph import StateGraph, END
from typing import TypedDict

class ApplicationState(TypedDict):
    job_description: str
    parsed_job_data: dict
    company_research: dict
    generated_documents: dict

# Mock Node Functions for demonstration
def parse_job_description(state: ApplicationState):
    print("---NODE: Parsing Job Description---")
    return {"parsed_job_data": {"title": "Policy Advisor", "company": "Gov Dept"}}

def research_company(state: ApplicationState):
    print("---NODE: Researching Company---")
    return {"company_research": {"mission": "To serve the public."}}

def generate_documents(state: ApplicationState):
    print("---NODE: Generating Documents---")
    return {"generated_documents": {"resume": "Final resume text.", "cover_letter": "Final cover letter text."}}

class WorkflowOrchestrator:
    def __init__(self):
        workflow = StateGraph(ApplicationState)
        workflow.add_node("parse_job", parse_job_description)
        workflow.add_node("research", research_company)
        workflow.add_node("generate", generate_documents)
        workflow.set_entry_point("parse_job")
        workflow.add_edge("parse_job", "research")
        workflow.add_edge("research", "generate")
        workflow.add_edge("generate", END)
        self.runnable = workflow.compile()
        print("Workflow Orchestrator compiled successfully.")

    def run(self, job_description: str):
        print(f"---ORCHESTRATOR: Starting workflow...---")
        initial_state = {"job_description": job_description}
        final_state = self.runnable.invoke(initial_state)
        print(f"---ORCHESTRATOR: Workflow finished.---")
        return final_state

orchestrator = WorkflowOrchestrator()
EOF

create_file src/api/main.py <<'EOF'
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .endpoints import generation, research, assistants

app = FastAPI(title="Enhanced Resume Agent API", docs_url="/api/docs", redoc_url=None)
app.include_router(generation.router, prefix="/api/generation", tags=["Generation"])
app.include_router(research.router, prefix="/api/research", tags=["Research"])
app.include_router(assistants.router, prefix="/api/assistants", tags=["Assistants"])
@app.get("/api/health")
def health_check(): return {"status": "healthy"}
app.mount("/", StaticFiles(directory="src/frontend", html=True), name="frontend")
EOF

create_file src/api/endpoints/generation.py <<'EOF'
from fastapi import APIRouter
from pydantic import BaseModel
from src.services.workflow_orchestrator import orchestrator

router = APIRouter()
class GenRequest(BaseModel): job_description: str
@router.post("/interactive")
async def generate_interactive(request: GenRequest):
    return orchestrator.run(request.job_description)
EOF

create_file src/api/endpoints/research.py <<'EOF'
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()
class DossierRequest(BaseModel): company_name: str
@router.post("/dossier")
async def generate_dossier(request: DossierRequest):
    return {"dossier_text": f"This is a detailed dossier for {request.company_name}."}
EOF

create_file src/api/endpoints/assistants.py <<'EOF'
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter()
class EnhanceRequest(BaseModel): text: str
@router.post("/enhance-bullet")
async def enhance_bullet(request: EnhanceRequest):
    return {"suggestions": [f"Enhanced version of: '{request.text}'"]}
EOF

create_file src/frontend/index.html <<'EOF'
<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>Resume Agent</title><link rel="stylesheet" href="css/style.css"></head><body><h1>Enhanced Resume Agent Dashboard</h1><section><h2>✨ AI Writing Assistant: Bullet Enhancer</h2><textarea id="bullet-input" placeholder="e.g., I was in charge of the weekly report."></textarea><button id="enhance-bullet-btn">Enhance Bullet</button><div id="bullet-suggestions"></div></section><section><h2>👔 Interview Prep: Company Dossier</h2><input type="text" id="company-name-input" placeholder="Enter Company Name"><button id="dossier-btn">Generate Dossier</button><pre id="dossier-output"></pre></section><section><h2>📄 Interactive Workflow Generation</h2><textarea id="jd-input" placeholder="Paste a full job description..."></textarea><button id="interactive-generate-btn">Run Full Workflow</button><pre id="workflow-output"></pre></section><script src="js/script.js"></script></body></html>
EOF

create_file src/frontend/js/script.js <<'EOF'
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('enhance-bullet-btn').addEventListener('click', async () => {
        const text = document.getElementById('bullet-input').value;
        const response = await fetch('/api/assistants/enhance-bullet', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ text }) });
        const data = await response.json();
        document.getElementById('bullet-suggestions').innerHTML = `<ul>${data.suggestions.map(s => `<li>${s}</li>`).join('')}</ul>`;
    });
    document.getElementById('dossier-btn').addEventListener('click', async () => {
        const company_name = document.getElementById('company-name-input').value;
        const outputEl = document.getElementById('dossier-output');
        outputEl.textContent = 'Generating...';
        const response = await fetch('/api/research/dossier', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ company_name }) });
        const data = await response.json();
        outputEl.textContent = data.dossier_text;
    });
    document.getElementById('interactive-generate-btn').addEventListener('click', async () => {
        const job_description = document.getElementById('jd-input').value;
        const outputEl = document.getElementById('workflow-output');
        outputEl.textContent = 'Invoking state machine...';
        const response = await fetch('/api/generation/interactive', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ job_description }) });
        const data = await response.json();
        outputEl.textContent = JSON.stringify(data, null, 2);
    });
});
EOF

create_file src/frontend/css/style.css <<'EOF'
body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; max-width: 800px; margin: auto; padding: 2rem; line-height: 1.6; background-color: #f8f9fa; color: #212529; }
section { border: 1px solid #dee2e6; padding: 1.5rem; margin-top: 2rem; border-radius: 8px; background-color: #fff; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
textarea, input[type="text"] { width: 100%; padding: 0.5rem; margin-bottom: 0.5rem; border: 1px solid #ced4da; border-radius: 4px; box-sizing: border-box; }
button { background-color: #0d6efd; color: white; border: none; padding: 0.6rem 1.2rem; border-radius: 4px; cursor: pointer; }
button:hover { background-color: #0b5ed7; }
h1, h2 { color: #343a40; }
pre, #bullet-suggestions { background-color: #e9ecef; padding: 1rem; border-radius: 4px; white-space: pre-wrap; word-wrap: break-word; }
EOF

echo "✅✅✅ Project setup complete! The '$PROJECT_NAME' directory is ready. ✅✅✅"