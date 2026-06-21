from app.pdf_reader import extract_text_from_pdf
from app.chunker import chunk_text
from app.vector_store import VectorStore

pdf_path = "uploads/cv.pdf"

text = extract_text_from_pdf(pdf_path)
chunks = chunk_text(text, chunk_size=1200, overlap=200)

vector_store = VectorStore()
vector_store.build_index(chunks)
question = "Programmiersprachen Python SQL Java Kotlin C R Assembler"
results = vector_store.search(question)

print("Question:", question)
print("\nRelevant chunks:\n")

for i, chunk in enumerate(results, start=1):
    print(f"--- Chunk {i} ---")
    print(chunk)
    print()