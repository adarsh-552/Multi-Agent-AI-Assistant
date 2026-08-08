from sentence_transformers import SentenceTransformer
import faiss

model = SentenceTransformer("all-MiniLM-L6-v2")

documents = [
    "Python is a programming language.",
    "Machine Learning uses data.",
    "Cricket is a popular sport."
]

embeddings = model.encode(documents)

dimension = embeddings.shape[1]

index = faiss.IndexFlatL2(dimension)

index.add(embeddings)

query = "Tell me about Python"

query_embedding = model.encode([query])

distance, index_result = index.search(query_embedding, k=1)

print("Most Similar Document:")

print(documents[index_result[0][0]])