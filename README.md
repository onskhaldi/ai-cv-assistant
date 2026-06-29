# CV Search App

A local, privacy-friendly web application for uploading PDF CVs and asking questions about their content.

The app extracts text from a PDF CV, detects common CV sections, builds a local semantic search index, and returns short structured answers based only on the uploaded document.

## Screenshot

![CV Search App Demo](docs/screenshots/cv-search-app-demo.png)

## Overview

CV Search App is a local portfolio project that demonstrates document processing, semantic search, and structured information extraction from PDF CVs.

Instead of sending CV content to an external language model API, the application processes the document locally. It uses PDF text extraction, section-aware parsing, local embeddings, and structured extraction to answer questions about the uploaded CV.

## Features

* Upload PDF CVs locally
* Extract text from PDF files using PyMuPDF
* Detect common CV sections such as work experience, education, projects, skills, tools, and languages
* Build a local semantic search index with Sentence Transformers
* Return short, structured answers based on the uploaded CV
* Show evidence/context for answers
* Delete uploaded PDF files after indexing
* No OpenAI API
* No external LLM API
* No API keys required
* Docker support
* Simple web interface built with HTML, CSS, and JavaScript

## Tech Stack

* Python
* FastAPI
* PyMuPDF
* Sentence Transformers
* NumPy
* Docker
* HTML


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
```

## Project Structure

```text
cv-search-app/
├── app/
│   ├── main.py
│   ├── pdf_reader.py
│   ├── chunker.py
│   ├── vector_store.py
│   ├── rag.py
│   └── static/
│       └── index.html
├── docs/
│   └── screenshots/
│       └── cv-search-app-demo.png
├── Dockerfile
├── requirements.txt
├── README.md
└── .gitignore
```

## Run Locally

Clone the repository:

```bash
git clone https://github.com/onskhaldi/cv-search-app.git
cd cv-search-app
```

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the application:

```bash
python -m uvicorn app.main:app --reload
```

Open the app in your browser:

```text
http://127.0.0.1:8000
```

## Run with Docker

Build the Docker image:

```bash
docker build -t cv-search-app .
```

Run the container:

```bash
docker run -p 7860:7860 cv-search-app
```

Open the app in your browser:

```text
http://127.0.0.1:7860
```

## How to Test the App

After starting the application locally, open the app in your browser:

```text
http://127.0.0.1:8000
```

### Test with the Web Interface

1. Prepare a small sample CV as a PDF file.
2. Open the app in your browser.
3. Upload the PDF using the upload form.
4. Wait until the app confirms that the CV was indexed.
5. Ask questions such as:

```text
What education does this candidate have?
What projects are mentioned in this CV?
What tools and technologies does this candidate know?
What languages does this candidate speak?
What work experience does this candidate have?
```

The app should return a short structured answer based only on the uploaded CV.

> Note: Use only test or sample CVs. Do not upload sensitive personal documents.

### Test with the API

Check if the app is running:

```bash
curl http://127.0.0.1:8000/health
```

Upload a sample PDF CV:

```bash
curl -X POST \
  -F "file=@/path/to/sample-cv.pdf" \
  http://127.0.0.1:8000/upload-cv
```

Replace `/path/to/sample-cv.pdf` with the path to your local test PDF.

Ask a question:

```bash
curl -X POST \
  http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What projects are mentioned in this CV?"}'
```

### Expected Result

A successful test should show that:

* the PDF uploads successfully
* the CV text is extracted
* the document is indexed locally
* questions return answers based on the uploaded CV
* the uploaded PDF is deleted after indexing

### Troubleshooting

If the browser cannot connect, make sure the server is running:

```bash
python -m uvicorn app.main:app --reload
```

If the app cannot answer questions, upload a CV first.

If PDF extraction fails, try a text-based PDF instead of a scanned image-only PDF.

## API Endpoints

### Health Check

```http
GET /health
```

Returns the current app status and whether a CV is loaded.

### Upload CV

```http
POST /upload-cv
```

Uploads a PDF CV, extracts its text, creates local chunks, builds the semantic index, and deletes the uploaded file after indexing.

### Ask Question

```http
POST /ask
```

Accepts a question and returns a structured answer based on the uploaded CV.

Example request body:

```json
{
  "question": "What projects are mentioned in this CV?"
}
```

## Privacy

This project is designed to run locally.

* Upload only test or sample CVs.
* Uploaded PDF files are processed temporarily.
* Uploaded files are deleted after indexing.
* CV content is not sent to external AI APIs.
* No OpenAI API key is used.
* No external LLM API is used.
* No public deployment is required.

## Security Notes

The application includes basic safeguards for local use:

* Only PDF uploads are accepted.
* Uploaded files are size-limited.
* Uploaded files are deleted after text extraction and indexing.
* Local folders such as virtual environments, uploaded files, caches, and private PDFs are ignored by Git.

## Limitations

This project is built for local portfolio demonstration and learning purposes.

Current limitations:

* It works best with text-based PDFs, not scanned image-only PDFs.
* CV formatting can affect extraction quality.
* The app does not perform OCR.
* The app does not use a generative language model.
* Answers are extracted and structured from the uploaded CV content.

## Portfolio Summary

CV Search App is a local semantic search project for PDF CVs. It demonstrates PDF parsing, document preprocessing, section-aware chunking, local embedding-based retrieval, structured answer extraction, privacy-aware file handling, and FastAPI backend development.

## License

This project is intended for educational and portfolio use.

---

## Testing

![Tests](https://github.com/onskhaldi/cv-search-app/actions/workflows/test.yml/badge.svg)

The project includes a pytest test suite covering the core CV search pipeline.

### Run locally

```bash
python -m pip install -r requirements.txt
python -m pip install pytest
python -m pytest -v
```

### Current test coverage

| Module | What is tested |
|---|---|
| `chunker.py` | Empty input, whitespace-only input, section headers, multiple sections, long section splitting, chunk-size behavior, return types |
| `vector_store.py` | Empty index, index building, result structure, numeric scores, relevance, `top_k` limits, index rebuild behavior, multilingual query expansion |
| `pdf_reader.py` | Missing file handling, non-PDF input validation, documented fixture-based edge cases |

### Known limitations documented in tests

- Scanned/image-based PDFs return no machine-readable text because OCR is not implemented.
- Real fixture-based PDF tests are skipped until a sample CV PDF is added under `tests/fixtures/`.
- The vector-store unit tests use a deterministic fake embedding model to avoid slow or flaky model downloads in CI.
