"""
agent_server.py — Bellissimo Agent Server
==========================================
A FastAPI server that wraps agent.py and exposes all agents as HTTP endpoints.

WHY THIS FILE EXISTS:
    agent.py is a great script. But a script only runs when you run it.
    This server makes every agent always-on, trigger-able from anywhere:
    - A form submission fires POST /scope → agent runs → result stored
    - A Zapier/Make webhook fires any agent on a schedule
    - You call GET /jobs/{id} from your phone to check the result
    - Multiple agents run in parallel — no waiting in line

ASYNC JOB PATTERN:
    Agents take 30–60 seconds (multiple Anthropic API round-trips).
    Synchronous HTTP would time out webhooks and block the server.
    Instead: submit a job → get a job_id → poll GET /jobs/{id} until done.

DEPLOY TO RAILWAY:
    1. Push this repo to GitHub
    2. Connect repo to Railway (railway.app)
    3. Set env vars: ANTHROPIC_API_KEY, SERVER_API_KEY
    4. Railway detects requirements.txt and deploys automatically
    5. Your agents are live at https://your-app.railway.app

AUTHENTICATION:
    All endpoints (except /health and /) require:
    Header: X-API-Key: <SERVER_API_KEY from .env>
"""

import asyncio
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Optional

from dotenv import load_dotenv
from fastapi import BackgroundTasks, Depends, FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from agent import run_agent

load_dotenv()

# =============================================================================
# APP SETUP
# =============================================================================

app = FastAPI(
    title="Bellissimo Agent Server",
    description="Always-on AI agents for Bellissimo AI Labs and SustainCFO",
    version="1.0.0",
)

SERVER_API_KEY = os.getenv("SERVER_API_KEY")


# =============================================================================
# AUTHENTICATION
# =============================================================================

def require_api_key(x_api_key: str = Header(...)):
    """
    Dependency: validates X-API-Key header on every protected endpoint.
    WHY Header auth: simple, works with Zapier/Make/curl without OAuth setup.
    """
    if not SERVER_API_KEY:
        raise HTTPException(status_code=500, detail="SERVER_API_KEY not configured")
    if x_api_key != SERVER_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return x_api_key


# =============================================================================
# JOB STORE
# =============================================================================

@dataclass
class Job:
    """
    Represents one agent run — from submission through completion.
    WHY dataclass: simple, no ORM needed for MVP. Swap for Redis/DB later.
    """
    job_id: str
    agent: str                    # "reveal" or "xray"
    client_name: str
    context: str
    status: str                   # "pending" | "running" | "completed" | "failed"
    submitted_at: str
    completed_at: Optional[str] = None
    result: Optional[str] = None
    error: Optional[str] = None


# In-memory job store — survives for the lifetime of the server process.
# Upgrade path: replace with Redis or a SQLite file for persistence.
jobs: Dict[str, Job] = {}


def _now() -> str:
    """Return current UTC time as ISO 8601 string."""
    return datetime.now(timezone.utc).isoformat()


# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class AgentRequest(BaseModel):
    client_name: str
    context: str = ""


class JobSubmittedResponse(BaseModel):
    job_id: str
    status: str
    agent: str
    client_name: str
    submitted_at: str
    poll_url: str


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    agent: str
    client_name: str
    submitted_at: str
    completed_at: Optional[str]
    result: Optional[str]
    error: Optional[str]


# =============================================================================
# BACKGROUND RUNNER
# =============================================================================

async def run_agent_background(job_id: str, mode: str):
    """
    Runs the agent in a thread pool so the event loop stays unblocked.

    WHY asyncio.to_thread():
        run_agent() is synchronous — it makes sequential blocking HTTP calls
        to the Anthropic API. asyncio.to_thread() runs it in a thread pool,
        so the FastAPI event loop can handle other requests while agents run.
        Multiple agents run truly in parallel this way.
    """
    job = jobs[job_id]
    job.status = "running"

    try:
        result = await asyncio.to_thread(
            run_agent,
            job.client_name,
            job.context,
            mode,
        )
        job.status = "completed"
        job.result = result
    except Exception as e:
        job.status = "failed"
        job.error = str(e)
    finally:
        job.completed_at = _now()


# =============================================================================
# ENDPOINTS
# =============================================================================

@app.get("/")
def root():
    """API info — no auth required. Good for a quick sanity check."""
    return {
        "service": "Bellissimo Agent Server",
        "version": "1.0.0",
        "agents": {
            "scope": "POST /scope — Bellissimo full business diagnostic",
            "xray":   "POST /xray   — SustainCFO financial deep-dive",
        },
        "docs": "/docs",
    }


@app.get("/health")
def health():
    """
    Health check — no auth required.
    Railway and Render ping this to verify the service is alive.
    """
    return {"status": "ok", "jobs_in_memory": len(jobs)}


@app.post("/scope", status_code=202)
async def submit_scope(
    request: AgentRequest,
    background_tasks: BackgroundTasks,
    _: str = Depends(require_api_key),
):
    """
    Submit a Bellissimo Scope diagnostic.

    Returns immediately with a job_id (202 Accepted).
    Poll GET /jobs/{job_id} until status == "completed".

    The Scope produces a 2-page intelligence report covering:
    - Business model clarity
    - Operational bottlenecks
    - AI readiness score
    - Digital presence gap
    - The big opportunity
    - Routing recommendation (SustainCFO vs Company OS)
    """
    job_id = f"scp_{uuid.uuid4().hex[:8]}"
    job = Job(
        job_id=job_id,
        agent="scope",
        client_name=request.client_name,
        context=request.context,
        status="pending",
        submitted_at=_now(),
    )
    jobs[job_id] = job

    # "reveal" is the internal mode name in agent.py — "scope" is the external brand name
    background_tasks.add_task(run_agent_background, job_id, "reveal")

    return JobSubmittedResponse(
        job_id=job_id,
        status="pending",
        agent="scope",
        client_name=request.client_name,
        submitted_at=job.submitted_at,
        poll_url=f"/jobs/{job_id}",
    )


@app.post("/xray", status_code=202)
async def submit_xray(
    request: AgentRequest,
    background_tasks: BackgroundTasks,
    _: str = Depends(require_api_key),
):
    """
    Submit a SustainCFO X-Ray financial diagnostic.

    Returns immediately with a job_id (202 Accepted).
    Poll GET /jobs/{job_id} until status == "completed".

    The X-Ray produces a CFO-grade financial report covering:
    - Revenue health and growth trends
    - Expense structure and red flags
    - Cash flow position and runway
    - Key financial ratios vs benchmarks
    - Top 3 priority recommendations
    """
    job_id = f"xry_{uuid.uuid4().hex[:8]}"
    job = Job(
        job_id=job_id,
        agent="xray",
        client_name=request.client_name,
        context=request.context,
        status="pending",
        submitted_at=_now(),
    )
    jobs[job_id] = job

    background_tasks.add_task(run_agent_background, job_id, "xray")

    return JobSubmittedResponse(
        job_id=job_id,
        status="pending",
        agent="xray",
        client_name=request.client_name,
        submitted_at=job.submitted_at,
        poll_url=f"/jobs/{job_id}",
    )


@app.get("/jobs/{job_id}")
def get_job(
    job_id: str,
    _: str = Depends(require_api_key),
):
    """
    Get the status and result of a job.

    Poll this endpoint after submitting a job.
    When status == "completed", result contains the full agent report.
    When status == "failed", error contains the exception message.
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")

    job = jobs[job_id]
    return JobStatusResponse(
        job_id=job.job_id,
        status=job.status,
        agent=job.agent,
        client_name=job.client_name,
        submitted_at=job.submitted_at,
        completed_at=job.completed_at,
        result=job.result,
        error=job.error,
    )


@app.get("/jobs")
def list_jobs(
    status: Optional[str] = None,
    _: str = Depends(require_api_key),
):
    """
    List all jobs, optionally filtered by status.

    Query params:
        ?status=pending | running | completed | failed

    Useful for dashboards and monitoring. Returns newest jobs first.
    """
    job_list = list(jobs.values())

    if status:
        job_list = [j for j in job_list if j.status == status]

    # Newest first
    job_list.sort(key=lambda j: j.submitted_at, reverse=True)

    return {
        "total": len(job_list),
        "jobs": [
            {
                "job_id": j.job_id,
                "agent": j.agent,
                "client_name": j.client_name,
                "status": j.status,
                "submitted_at": j.submitted_at,
                "completed_at": j.completed_at,
            }
            for j in job_list
        ],
    }


# =============================================================================
# LOCAL DEV ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    import uvicorn

    print("\nBellissimo Agent Server — Local Dev")
    print("Docs: http://localhost:8000/docs")
    print("Health: http://localhost:8000/health\n")

    uvicorn.run("agent_server:app", host="0.0.0.0", port=8000, reload=True)
