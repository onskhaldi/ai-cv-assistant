# AI CV Assistant

AI CV Assistant is a web application that allows users to upload a CV in PDF format and ask natural language questions about the candidate's profile.

## Features

* Upload PDF resumes
* Automatic text extraction
* Document chunking
* Retrieval-based search
* Question answering over CV content
* Modern web interface built with HTML, CSS, and JavaScript
* FastAPI backend

## Example Questions

* What work experience does this candidate have?
* What projects are mentioned in the CV?
* What programming languages does the candidate know?
* What tools and technologies are listed?
* What education does the candidate have?

## Technology Stack

* Python
* FastAPI
* Scikit-Learn
* HTML
* CSS
* JavaScript

## Project Structure

```text
app/
├── main.py
├── pdf_reader.py
├── chunker.py
├── vector_store.py
├── rag.py
└── static/
    └── index.html
```

## Author

Ones Khaldi

## License

© 2026 Ones Khaldi. All rights reserved.
<img width="627" height="563" alt="Screenshot 2026-06-16 at 2 21 42 AM" src="https://github.com/user-attachments/assets/8aa3fae9-128c-4e65-b6f9-2161e80f9c57" />

## Privacy

This project is intended as a portfolio/demo application.

- Upload only test or sample CVs.
- Uploaded PDF files are processed temporarily.
- Uploaded files are deleted after indexing.
- CV content is not sent to external AI APIs.
- No OpenAI API key or external LLM API is used.
- Do not upload sensitive personal documents to the public demo.
