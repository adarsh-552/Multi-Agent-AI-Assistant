from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

sentence = "Python Full Stack Developer"

embedding = model.encode(sentence)

print("Embedding Length:", len(embedding))

print("\nFirst 10 Values:\n")

print(embedding[:10])