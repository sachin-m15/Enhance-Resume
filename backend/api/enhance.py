import os
import cgi
import tempfile
from http.server import BaseHTTPRequestHandler
from .workflow import run_workflow
import json


class handler(BaseHTTPRequestHandler):
    """
    Vercel Serverless Function to handle resume enhancement requests.
    This function acts as the main API endpoint.
    """

    def do_POST(self):
        """
        Handles POST requests containing a PDF resume for enhancement.
        """
        # Create a temporary directory to store files
        with tempfile.TemporaryDirectory() as temp_dir:
            input_pdf_path = None
            output_pdf_path = None
            try:
                # Parse the multipart/form-data request
                form = cgi.FieldStorage(
                    fp=self.rfile,
                    headers=self.headers,
                    environ={
                        "REQUEST_METHOD": "POST",
                        "CONTENT_TYPE": self.headers["Content-Type"],
                    },
                )

                if "resume" not in form:
                    self.send_error(
                        400, "Bad Request: 'resume' file not found in form data."
                    )
                    return

                file_item = form["resume"]

                if not file_item.filename or not file_item.file:
                    self.send_error(
                        400, "Bad Request: Uploaded file is empty or invalid."
                    )
                    return

                # Save the uploaded PDF to a temporary file
                input_pdf_path = os.path.join(temp_dir, "input_resume.pdf")
                with open(input_pdf_path, "wb") as f:
                    f.write(file_item.file.read())

                # Run the LangGraph workflow to enhance the resume
                print("Starting resume enhancement workflow...")
                output_pdf_path = run_workflow(input_pdf_path)
                print(f"Workflow finished. Enhanced resume at: {output_pdf_path}")

                # Read the generated PDF and send it back in the response
                with open(output_pdf_path, "rb") as f:
                    pdf_content = f.read()

                self.send_response(200)
                self.send_header("Content-Type", "application/pdf")
                self.send_header(
                    "Content-Disposition", 'attachment; filename="enhanced_resume.pdf"'
                )
                self.end_headers()
                self.wfile.write(pdf_content)

            except Exception as e:
                print(f"An error occurred: {e}")
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                error_response = json.dumps(
                    {"error": "An internal server error occurred.", "details": str(e)}
                )
                self.wfile.write(error_response.encode("utf-8"))
