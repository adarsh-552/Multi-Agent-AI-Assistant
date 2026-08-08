from rag.rag_pipeline import create_chunks

chunks = create_chunks("uploads/sample.pdf")

print("Total Chunks:", len(chunks))

print("\nFirst Chunk:\n")

print(chunks[0])