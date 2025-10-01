import os
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

# CORRECTED: Changed to a relative import within the 'backend' package
from .utils import get_ats_score, generate_pdf_from_text
from dotenv import load_dotenv

# --- Environment Variables ---
load_dotenv()

if os.getenv("GROQ_API_KEY") is None:
    raise ValueError(
        "Please set the GROQ_API_KEY environment variable in your .env file or Vercel project settings."
    )

# --- Models ---
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.2,
    groq_api_key=os.getenv("GROQ_API_KEY"),
)


# --- State Definition ---
class ResumeState(TypedDict):
    original_resume_text: str
    original_ats_score: int
    enhancement_suggestions: str
    enhanced_resume_text: str
    enhanced_ats_score: int
    final_pdf_path: Annotated[str, "The path to the generated PDF file"]


# --- Graph Nodes ---
async def score_original_resume(state: ResumeState):
    """Scores the original resume text against an ATS."""
    print("---SCORING ORIGINAL RESUME---")
    resume_text = state["original_resume_text"]
    score = await get_ats_score(resume_text)
    print(f"Original ATS Score: {score}")
    return {"original_ats_score": score}


async def get_enhancement_suggestions(state: ResumeState):
    """Uses the LLM to generate suggestions for improving the resume."""
    print("---GETTING ENHANCEMENT SUGGESTIONS---")
    resume_text = state["original_resume_text"]

    prompt = f"""
    Based on the following resume text, analyze it for ATS optimization.
    Identify weaknesses in terms of keywords, action verbs, formatting clarity, and overall structure.
    Provide a concise list of suggestions for improvement.

    Resume Text:
    ---
    {resume_text}
    ---
    Suggestions:
    """

    response = await llm.ainvoke([HumanMessage(content=prompt)])
    suggestions = response.content
    print(f"Enhancement Suggestions:\n{suggestions}")
    return {"enhancement_suggestions": suggestions}


async def enhance_resume_text(state: ResumeState):
    """Uses the LLM to rewrite the resume based on suggestions."""
    print("---ENHANCING RESUME TEXT---")
    resume_text = state["original_resume_text"]
    suggestions = state["enhancement_suggestions"]

    prompt = f"""
    Rewrite and enhance the following resume text to be highly optimized for Applicant Tracking Systems (ATS).
    Incorporate the following suggestions.
    - Use strong action verbs.
    - Integrate relevant keywords for common job roles (like software engineering, marketing, etc.).
    - Ensure a clean, parsable structure with clear headings (e.g., "Experience", "Education", "Skills").
    - Quantify achievements with metrics where possible.
    - Do not invent information, only rephrase and restructure existing content. The output should only be the enhanced resume text.

    Original Resume:
    ---
    {resume_text}
    ---

    Suggestions for Improvement:
    ---
    {suggestions}
    ---

    Enhanced Resume Text:
    """

    response = await llm.ainvoke([HumanMessage(content=prompt)])
    enhanced_text = response.content
    print(f"Enhanced Resume Text generated.")
    return {"enhanced_resume_text": enhanced_text}


async def score_enhanced_resume(state: ResumeState):
    """Scores the new, enhanced resume."""
    print("---SCORING ENHANCED RESUME---")
    enhanced_text = state["enhanced_resume_text"]
    score = await get_ats_score(enhanced_text)
    print(f"Enhanced ATS Score: {score}")
    return {"enhanced_ats_score": score}


async def generate_final_pdf(state: ResumeState):
    """Generates the final PDF from the enhanced resume text."""
    print("---GENERATING FINAL PDF---")
    enhanced_text = state["enhanced_resume_text"]
    file_path = await generate_pdf_from_text(enhanced_text)
    print(f"Final PDF generated at: {file_path}")
    return {"final_pdf_path": file_path}


# --- Graph Definition ---
workflow = StateGraph(ResumeState)

workflow.add_node("score_original", score_original_resume)
workflow.add_node("get_suggestions", get_enhancement_suggestions)
workflow.add_node("enhance_resume", enhance_resume_text)
workflow.add_node("score_enhanced", score_enhanced_resume)
workflow.add_node("generate_pdf", generate_final_pdf)

workflow.set_entry_point("score_original")
workflow.add_edge("score_original", "get_suggestions")
workflow.add_edge("get_suggestions", "enhance_resume")
workflow.add_edge("enhance_resume", "score_enhanced")
workflow.add_edge("score_enhanced", "generate_pdf")
workflow.add_edge("generate_pdf", END)

resume_enhancement_graph = workflow.compile()
