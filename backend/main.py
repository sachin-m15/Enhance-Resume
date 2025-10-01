import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from .graph import resume_enhancement_graph
from .utils import extract_text_from_pdf

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for simplicity, restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Intelligent Resume Enhancement System API is running."}


@app.post("/enhance-resume/")
async def enhance_resume(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400, detail="Invalid file type. Only PDF is accepted."
        )

    try:
        # Save the uploaded file temporarily
        temp_file_path = f"/tmp/{file.filename}"
        with open(temp_file_path, "wb") as buffer:
            buffer.write(await file.read())

        # Process the resume
        inputs = {"resume_path": temp_file_path}
        result = resume_enhancement_graph.invoke(inputs)

        original_score = result.get("original_ats_score", 0)
        enhanced_score = result.get("enhanced_ats_score", 100)
        pdf_bytes = result.get("enhanced_pdf_bytes")

        if not pdf_bytes:
            raise HTTPException(
                status_code=500, detail="Failed to generate enhanced PDF."
            )

        # Clean up the temporary file
        os.remove(temp_file_path)

        headers = {
            "Content-Disposition": 'attachment; filename="enhanced_resume.pdf"',
            "X-Original-ATS-Score": str(original_score),
            "X-Enhanced-ATS-Score": str(enhanced_score),
            "Access-Control-Expose-Headers": "X-Original-ATS-Score, X-Enhanced-ATS-Score",
        }

        return Response(
            content=pdf_bytes, media_type="application/pdf", headers=headers
        )

    except Exception as e:
        # Clean up in case of error
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise HTTPException(status_code=500, detail=str(e))
