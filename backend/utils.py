import pdfplumber
from fpdf import FPDF
import uuid
import asyncio
import os

# --- PDF Parsing ---
async def parse_pdf_text(file_path: str) -> str:
    """Extracts text from an uploaded PDF file."""
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error parsing PDF: {e}")
        return ""
    return text

# --- ATS Score Simulation ---
async def get_ats_score(resume_text: str) -> int:
    """
    Simulates an ATS score based on keywords and text length.
    This is a placeholder for a real ATS scoring API.
    """
    await asyncio.sleep(1) # Simulate network delay
    
    # Simple scoring logic (example)
    score = 0
    keywords = ["experience", "education", "skills", "python", "fastapi", "project", "team", "developed"]
    
    text_lower = resume_text.lower()
    for keyword in keywords:
        if keyword in text_lower:
            score += 10
            
    # Score based on length
    if len(resume_text) > 500:
        score += 10
    if len(resume_text) > 1000:
        score += 10
        
    return min(score, 100)

# --- PDF Generation ---
async def generate_pdf_from_text(text: str) -> str:
    """
    Generates a new PDF document from the enhanced resume text.
    Saves the file to the /tmp directory, which is writable on Vercel.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Add text to PDF, handling multiple lines
    for line in text.split('\n'):
        pdf.cell(200, 10, txt=line, ln=True, align='L')
        
    # **FIX**: Use the /tmp/ directory for Vercel's writable filesystem
    file_name = f"{uuid.uuid4()}.pdf"
    file_path = os.path.join("/tmp", file_name)
    
    try:
        pdf.output(file_path)
        print(f"PDF successfully generated at: {file_path}")
        return file_path
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return ""

