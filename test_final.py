from rag.rag_pipeline import create_vector_store, ask_pdf

index, chunks = create_vector_store("uploads/sample.pdf")

while True:

    question = input("\nAsk Question (type exit to quit): ")

    if question.lower() == "exit":
        break

    answer = ask_pdf(question, index, chunks)

    print("\nAI Answer:\n")

    print(answer)