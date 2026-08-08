from rag.rag_pipeline import create_vector_store, search_document

index, chunks = create_vector_store("uploads/sample.pdf")

question = input("Ask Question: ")

results = search_document(question, index, chunks)

print("\nMost Relevant Chunks:\n")

for chunk in results:
    print("--------------------------------")
    print(chunk)