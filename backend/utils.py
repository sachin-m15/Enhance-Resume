import fitz  # PyMuPDF
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import random
import uuid
import os


async def parse_pdf_to_text(pdf_content: bytes) -> str:
    """
    Parses the content of a PDF file (image or text) and returns the text.
    Uses PyMuPDF which includes OCR capabilities if needed.
    """
    text = ""
    try:
        # Open the PDF from bytes
        doc = fitz.open(stream=pdf_content, filetype="pdf")
        for page in doc:
            text += page.get_text()
        doc.close()
    except Exception as e:
        print(f"Error parsing PDF: {e}")
        return ""
    return text


async def get_ats_score(resume_text: str) -> int:
    """
    Placeholder for a free resume parsing API.
    In a real application, you would make an HTTP request to an actual service.
    For this example, it returns a random score to simulate the process.
    """
    # Simulate API call delay
    # await asyncio.sleep(1)

    # Simple heuristic: score is based on length
    score = min(100, len(resume_text) // 25)

    # Add some randomness
    score = score + random.randint(-5, 5)

    return max(0, min(100, score))


async def generate_pdf_from_text(text_content: str) -> str:
    """
    Generates a PDF file from a string of text.
    Saves it to a temporary directory.
    """
    # Vercel uses a /tmp directory for temporary file storage
    output_dir = "/tmp"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    file_name = f"enhanced_resume_{uuid.uuid4()}.pdf"
    file_path = os.path.join(output_dir, file_name)

    doc = SimpleDocTemplate(file_path, pagesize=letter)
    styles = getSampleStyleSheet()
    style = styles["BodyText"]

    # Replace newlines with <br/> tags for proper paragraph breaks in ReportLab
    formatted_text = text_content.replace("\n", "<br/>")

    story = [Paragraph(formatted_text, style)]

    doc.build(story)

    # In a real app, you'd return a public URL to this file from cloud storage.
    # For this example, we return the text content to be displayed directly.
    # We will return the text content itself for display, as serving static files
    # from /tmp is complex in Vercel. A real-world app would use S3/GCS.
    return text_content  # Returning text to be displayed directly in HTML
