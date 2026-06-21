# CV Search App

A local, privacy-friendly web application for uploading PDF CVs and asking questions about their content.

The app extracts text from a PDF CV, detects common CV sections, builds a local semantic search index, and returns short structured answers based only on the uploaded document.

## Screenshot

![CV Search App Demo](docs/screenshots/cv-search-app-demo.png)

## Overview

CV Search App is a local portfolio project that demonstrates document processing, semantic search, and structured information extraction from PDF CVs.

Instead of sending CV content to an external language model API, the application processes the document locally. It uses PDF text extraction, section-aware parsing, local embeddings, and structured extraction to answer questions about the uploaded CV.

## Features

- Upload PDF CVs locally
- Extract text from PDF files using PyMuPDF
- Detect common CV sections such as work experience, education, projects, skills, tools, and languages
- Build a local semantic search index with Sentence Transformers
- Return short, structured answers based on the uploaded CV
- Show evidence/context for answers
- Delete uploaded PDF files after indexing
- No OpenAI API
- No external LLM API
- No API keys required
- Docker support
- Simple web interface built with HTML, CSS, and JavaScript

## Tech Stack

- Python
- FastAPI
- PyMuPDF
- Sentence Transformers
- NumPy
- Docker
- HTML
- CSS
- JavaScript

## How It Works

1. The user uploads a PDF CV locally.
2. The backend extracts text from the PDF using PyMuPDF.
3. The extracted text is cleaned and split into CV-specific sections.
4. Local embeddings are created with Sentence Transformers.
5. The user asks a natural-language question.
6. The app retrieves relevant CV sections and applies structured extraction.
7. A short answer is returned based only on the uploaded CV.
8. The uploaded PDF file is deleted after indexing.

## Example Questions

```text
What work experience does this candidate have?
What education does this candidate have?
What projects are mentioned in this CV?
What tools and technologies does this candidate know?
What languages does this candidate speak?
