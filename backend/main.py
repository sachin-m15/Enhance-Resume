import os
import uuid
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
import asyncio
from typing import Dict

# These relative imports are correct for this structure
from .graph import resume_enhancement_graph
from .utils import parse_pdf_to_text

# --- App Initialization ---
app = FastAPI()

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
    # CORRECTED: Path is now relative to the backend/ directory
    with open("frontend/index.html") as f:
        return HTMLResponse(content=f.read(), status_code=200)


# --- Helper Function to run the graph ---
async def run_graph_for_task(task_id: str, file_content: bytes):
    """
    Runs the LangGraph resume enhancement process asynchronously.
    """
    try:
        tasks[task_id]["status"] = "parsing_resume"
        # Step 1: Parse PDF to text
        resume_text = await parse_pdf_to_text(file_content)
        if not resume_text or len(resume_text) < 50:
            tasks[task_id]["status"] = "error"
            tasks[task_id]["result"] = "Failed to parse resume or content too short."
            return

        initial_state = {"original_resume_text": resume_text}

        tasks[task_id]["status"] = "enhancing_resume"

        # Step 2: Run the graph
        final_state = await resume_enhancement_graph.ainvoke(initial_state)

        tasks[task_id]["status"] = "completed"
        tasks[task_id]["result"] = final_state

    except Exception as e:
        print(f"Error during task {task_id}: {e}")
        tasks[task_id]["status"] = "error"
        tasks[task_id]["result"] = str(e)


# --- API Endpoints ---
@app.post("/upload/")
async def upload_resume(file: UploadFile = File(...)):
    """
    Handles resume upload, initiates the enhancement process, and returns a task ID.
    """
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400, detail="Invalid file type. Please upload a PDF."
        )

    task_id = str(uuid.uuid4())
    tasks[task_id] = {"status": "processing"}

    file_content = await file.read()

    # Run the graph in the background
    asyncio.create_task(run_graph_for_task(task_id, file_content))

    return {"task_id": task_id}


@app.get("/status/{task_id}")
async def get_status(task_id: str):
    """
    Checks the status of a given task.
    """
    task = tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return JSONResponse(content=task)
