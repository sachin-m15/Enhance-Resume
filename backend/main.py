import os
import uuid
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
import asyncio
from typing import Dict

from .graph import resume_enhancement_graph
from .utils import parse_pdf_to_text

# --- App Initialization ---
app = FastAPI()

# This line is commented out as per our previous step to remove favicon logic
# app.mount("/static", StaticFiles(directory="frontend/static"), name="static")


# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for task status and results
tasks: Dict[str, Dict] = {}


# --- Static Files ---
@app.get("/", response_class=HTMLResponse)
async def read_root():
    # This path is correct for Vercel's build environment
    with open("frontend/index.html") as f:
        return HTMLResponse(content=f.read(), status_code=200)


# --- Helper Function to run the graph ---
async def run_graph_for_task(task_id: str, file_content: bytes):
    """
    Runs the LangGraph resume enhancement process asynchronously with a timeout.
    """
    try:
        tasks[task_id]["status"] = "parsing_resume"
        resume_text = await parse_pdf_to_text(file_content)
        if not resume_text or len(resume_text) < 50:
            tasks[task_id]["status"] = "error"
            tasks[task_id]["result"] = "Failed to parse resume or content too short."
            return

        initial_state = {"original_resume_text": resume_text}

        # New status update for better frontend feedback
        tasks[task_id]["status"] = "calling_ai"

        # Run the graph with a 15-second timeout to prevent silent fails on Vercel
        final_state = await asyncio.wait_for(
            resume_enhancement_graph.ainvoke(initial_state), timeout=15.0
        )

        tasks[task_id]["status"] = "completed"
        tasks[task_id]["result"] = final_state

    except asyncio.TimeoutError:
        print(f"Task {task_id} timed out.")
        tasks[task_id]["status"] = "error"
        tasks[task_id]["result"] = (
            "The AI process took too long to respond. This can happen on Vercel's free plan. Please try again."
        )
    except Exception as e:
        print(f"Error during task {task_id}: {e}")
        tasks[task_id]["status"] = "error"
        tasks[task_id]["result"] = str(e)


# --- API Endpoints ---
@app.post("/upload/")
async def upload_resume(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400, detail="Invalid file type. Please upload a PDF."
        )

    task_id = str(uuid.uuid4())
    tasks[task_id] = {"status": "processing"}
    file_content = await file.read()
    asyncio.create_task(run_graph_for_task(task_id, file_content))
    return {"task_id": task_id}


@app.get("/status/{task_id}")
async def get_status(task_id: str):
    task = tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return JSONResponse(content=task)
