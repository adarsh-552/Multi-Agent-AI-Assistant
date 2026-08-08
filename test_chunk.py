from agents.pdf_agent import read_pdf
from langchain_text_splitters import RecursiveCharacterTextSplitter

text = read_pdf("uploads/sample.pdf")

splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=50
)

chunks = splitter.split_text(text)

print(f"Total Chunks: {len(chunks)}")

print("\nFirst Chunk:\n")

print(chunks[0])