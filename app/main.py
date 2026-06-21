from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.chunker import chunk_text
from app.pdf_reader import extract_text_from_pdf
from app.rag import generate_answer
from app.vector_store import VectorStore


UPLOAD_DIR = Path("uploads")
MAX_FILE_SIZE_BYTES = 2 * 1024 * 1024  # 2 MB

UPLOAD_DIR.mkdir(exist_ok=True)

app = FastAPI(
    title="AI CV Assistant",
    description="Local-first semantic search over uploaded CV PDFs.",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

vector_store = VectorStore()
current_document = {
    "filename": None,
    "chunks_created": 0,
    "text": "",
}


class QuestionRequest(BaseModel):
    question: str


@app.get("/")
def home():
    return FileResponse("app/static/index.html")


@app.get("/health")
def health():
    return {
        "status": "ok",
        "document_loaded": current_document["filename"] is not None,
        "chunks_created": current_document["chunks_created"],
    }


@app.post("/upload-cv")
async def upload_cv(file: UploadFile = File(...)):
    if not file.filename:
        return {"error": "No file uploaded."}

    if not file.filename.lower().endswith(".pdf"):
        return {"error": "Only PDF files are allowed."}

    file_content = await file.read()

    if len(file_content) > MAX_FILE_SIZE_BYTES:
        return {"error": "File is too large. Maximum allowed size is 2 MB."}

    safe_filename = Path(file.filename).name
    file_path = UPLOAD_DIR / safe_filename

    try:
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)

        text = extract_text_from_pdf(str(file_path))

        if not text.strip():
            return {"error": "No readable text was found in the PDF."}

        chunks = chunk_text(text, chunk_size=650, overlap=0)
        vector_store.build_index(chunks)

        current_document["filename"] = safe_filename
        current_document["chunks_created"] = len(chunks)
        current_document["text"] = text

        return {
            "message": "CV uploaded and indexed successfully.",
            "filename": safe_filename,
            "chunks_created": len(chunks),
        }

    finally:
        if file_path.exists():
            os.remove(file_path)


@app.post("/ask")
def ask_question(request: QuestionRequest):
    if current_document["filename"] is None:
        return {
            "question": request.question,
            "answer": "Please upload a CV before asking questions.",
            "sources": [],
        }

    retrieved_chunks = vector_store.search(request.question, top_k=12)
    answer = generate_answer(request.question, retrieved_chunks, current_document.get("text", ""))

    return {
        "question": request.question,
        "answer": answer,
        "sources": retrieved_chunks,
    }
