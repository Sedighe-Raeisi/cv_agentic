import base64
import io
import os
import shutil
import tempfile

import pymupdf  # PyMuPDF
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image

from src.agent.graph import build_cv_agent

app = FastAPI(title="Agentic CV Web Engine", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def convert_pdf_to_base64_images(pdf_path: str) -> list[str]:
    """Renders PDF pages as compressed JPEG images encoded in base64."""
    doc = pymupdf.open(pdf_path)
    base64_images = []
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(matrix=pymupdf.Matrix(1.35, 1.35))
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=80)
        encoded_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
        base64_images.append(encoded_str)
        
    return base64_images


@app.post("/api/enrich")
async def enrich_cv_endpoint(
    file: UploadFile = File(...),
    github_username: str = Form(...),
    custom_prompt: str = Form(...),
    output_format: str = Form("latex")
):
    filename = file.filename.lower()
    file_bytes = await file.read()

    cv_text_template = ""
    base64_images = []

    # Dynamic file type detection
    if filename.endswith((".tex", ".txt")):
        # Path A: Raw text/LaTeX template processing
        cv_text_template = file_bytes.decode("utf-8")

    elif filename.endswith(".pdf"):
        # Path B: PDF rendered to images for Vision
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name
        
        base64_images = convert_pdf_to_base64_images(tmp_path)
        os.remove(tmp_path)

    elif filename.endswith((".png", ".jpg", ".jpeg")):
        # Path C: Direct image uploads
        encoded_str = base64.b64encode(file_bytes).decode("utf-8")
        base64_images.append(encoded_str)

    else:
        raise HTTPException(
            status_code=400, 
            detail="Unsupported file format. Upload .tex, .txt, .pdf, .png, or .jpg files."
        )

    # Initialize LangGraph workflow with detected inputs
    agent_app = build_cv_agent()
    initial_state = {
        "messages": [],
        "cv_text_template": cv_text_template,
        "cv_images_base64": base64_images,
        "github_username": github_username,
        "github_data": [],
        "custom_prompt": custom_prompt,
        "draft_cv": "",
        "validation_passed": False,
        "critique": "",
        "revision_count": 0
    }

    final_state = agent_app.invoke(initial_state)
    latex_content = final_state.get("draft_cv", "")

    return JSONResponse(content={
        "status": "success", 
        "latex_code": latex_content
    })