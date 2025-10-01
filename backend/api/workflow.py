import os
import tempfile
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from pypdf import PdfReader
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from dotenv import load_dotenv

# Load environment variables from .env.local
load_dotenv()


# --- 1. Define the State for the Graph ---
class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        original_resume_text: The extracted text from the user's PDF.
        ats_feedback: Mocked feedback from an ATS system.
        enhanced_resume_text: The rewritten resume text from the LLM.
        final_pdf_path: The file path of the newly generated PDF.
    """

    original_resume_text: str
    ats_feedback: str
    enhanced_resume_text: str
    final_pdf_path: str


# --- 2. Define the Nodes for the Graph ---


def parse_pdf(state, pdf_path):
    """
    Parses the text content from an uploaded PDF file.

    Args:
        state: The current graph state.
        pdf_path: The path to the PDF file to parse.

    Returns:
        A dictionary with the extracted text.
    """
    print("---PARSING PDF---")
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        print("PDF Parsed successfully.")
        return {"original_resume_text": text}
    except Exception as e:
        print(f"Error parsing PDF: {e}")
        raise


def get_ats_feedback(state):
    """
    Mocks a call to an ATS scoring service. In a real application,
    this would involve a call to an external API.

    Args:
        state: The current graph state.

    Returns:
        A dictionary with mocked ATS feedback.
    """
    print("---GETTING MOCKED ATS FEEDBACK---")
    # This is mocked feedback. A real system would have a more complex logic.
    feedback = (
        "ATS Score: 68/100. Feedback: Resume lacks quantifiable achievements. "
        "Use more action verbs. Some sections are too wordy. "
        "Consider adding a skills section with keywords relevant to the target job."
    )
    print(f"Mocked feedback generated: {feedback}")
    return {"ats_feedback": feedback}


def enhance_resume(state):
    """
    Uses the Groq LLM to rewrite and enhance the resume text.

    Args:
        state: The current graph state.

    Returns:
        A dictionary with the enhanced resume text.
    """
    print("---ENHANCING RESUME WITH GROQ LLM---")
    original_text = state["original_resume_text"]
    feedback = state["ats_feedback"]

    # Initialize the Groq Chat LLM
    llm = ChatGroq(model="llama3-70b-8192", temperature=0.2)

    prompt = f"""
    You are an expert resume writer and career coach for a top-tier recruitment agency.
    Your task is to rewrite and enhance a client's resume to make it highly effective and ATS-friendly.
    
    **ATS Feedback:**
    {feedback}

    **Original Resume Text:**
    ---
    {original_text}
    ---

    **Instructions:**
    1.  **Rewrite and Rephrase:** Do not just edit; completely rewrite the content to be more impactful.
    2.  **Action Verbs:** Start bullet points with strong, varied action verbs (e.g., "Orchestrated," "Engineered," "Spearheaded").
    3.  **Quantify Achievements:** Incorporate metrics and data to demonstrate impact (e.g., "Increased efficiency by 15%," "Managed a budget of $500k"). If exact numbers aren't present, you can suggest placeholders like "[Increased revenue by X%]" or "[Managed a team of Y people]".
    4.  **Clarity and Conciseness:** Eliminate jargon and wordiness. Make every sentence count.
    5.  **Professional Summary:** Add a compelling 3-4 line professional summary at the top if one is missing or weak.
    6.  **Formatting:** Use clean, professional formatting. Use standard section headers (e.g., "Professional Experience," "Education," "Skills," "Projects"). Use bullet points for job descriptions.
    7.  **Output:** Provide only the full, rewritten resume text. Do not include any preambles, apologies, or explanations. Just the final resume content.
    """

    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        enhanced_text = response.content
        print("Resume enhancement complete.")
        return {"enhanced_resume_text": enhanced_text}
    except Exception as e:
        print(f"Error calling LLM: {e}")
        raise


def generate_pdf(state):
    """
    Generates a new PDF document from the enhanced resume text.

    Args:
        state: The current graph state.

    Returns:
        A dictionary with the path to the newly created PDF.
    """
    print("---GENERATING NEW PDF---")
    enhanced_text = state["enhanced_resume_text"]

    # Create a temporary file for the output PDF
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    output_pdf_path = temp_file.name
    temp_file.close()

    try:
        doc = SimpleDocTemplate(output_pdf_path)
        styles = getSampleStyleSheet()
        story = []

        # Split text into paragraphs and add to the story
        for line in enhanced_text.split("\n"):
            if line.strip():  # Avoid empty lines creating extra space
                p = Paragraph(line, styles["Normal"])
                story.append(p)
            else:
                story.append(
                    Spacer(1, 0.1 * inch)
                )  # Add a bit of space for blank lines

        doc.build(story)
        print(f"New PDF generated at: {output_pdf_path}")
        return {"final_pdf_path": output_pdf_path}
    except Exception as e:
        print(f"Error generating PDF: {e}")
        raise


# --- 3. Define the Graph and Run Workflow ---


def run_workflow(pdf_path):
    """
    Builds the LangGraph and executes the resume enhancement process.

    Args:
        pdf_path: The path to the input PDF file.

    Returns:
        The file path of the final, enhanced PDF.
    """
    # Define a new graph
    workflow = StateGraph(GraphState)

    # Add the nodes
    workflow.add_node("parse_pdf", lambda state: parse_pdf(state, pdf_path))
    workflow.add_node("get_ats_feedback", get_ats_feedback)
    workflow.add_node("enhance_resume", enhance_resume)
    workflow.add_node("generate_pdf", generate_pdf)

    # Build the graph by setting the edges
    workflow.set_entry_point("parse_pdf")
    workflow.add_edge("parse_pdf", "get_ats_feedback")
    workflow.add_edge("get_ats_feedback", "enhance_resume")
    workflow.add_edge("enhance_resume", "generate_pdf")
    workflow.add_edge("generate_pdf", END)

    # Compile the graph into a runnable app
    app = workflow.compile()

    # Run the graph
    final_state = app.invoke({})

    return final_state["final_pdf_path"]
