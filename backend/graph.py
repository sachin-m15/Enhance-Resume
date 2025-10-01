import os
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from .utils import get_ats_score, generate_pdf_from_text  # Correct relative import
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
    print("---SCORING ORIGINAL RESUME---")
    resume_text = state["original_resume_text"]
    score = await get_ats_score(resume_text)
    return {"original_ats_score": score}


async def get_enhancement_suggestions(state: ResumeState):
    print("---GETTING ENHANCEMENT SUGGESTIONS---")
    resume_text = state["original_resume_text"]
    prompt = f"Based on the following resume text, analyze it for ATS optimization. Provide a concise list of suggestions for improvement.\n\nResume Text:\n---\n{resume_text}\n---\nSuggestions:"
    response = await llm.ainvoke([HumanMessage(content=prompt)])
    return {"enhancement_suggestions": response.content}


async def enhance_resume_text(state: ResumeState):
    print("---ENHANCING RESUME TEXT---")
    resume_text = state["original_resume_text"]
    suggestions = state["enhancement_suggestions"]
    prompt = f"Rewrite and enhance the following resume text to be highly optimized for Applicant Tracking Systems (ATS). Incorporate these suggestions: {suggestions}. Do not invent information. The output should only be the enhanced resume text.\n\nOriginal Resume:\n---\n{resume_text}\n---\nEnhanced Resume Text:"
    response = await llm.ainvoke([HumanMessage(content=prompt)])
    return {"enhanced_resume_text": response.content}


async def score_enhanced_resume(state: ResumeState):
    print("---SCORING ENHANCED RESUME---")
    enhanced_text = state["enhanced_resume_text"]
    score = await get_ats_score(enhanced_text)
    return {"enhanced_ats_score": score}


async def generate_final_pdf(state: ResumeState):
    print("---GENERATING FINAL PDF---")
    enhanced_text = state["enhanced_resume_text"]
    file_path = await generate_pdf_from_text(enhanced_text)
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
