from agents.pdf_agent import read_pdf
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from langchain_groq import ChatGroq
from config import GROQ_API_KEY

model = SentenceTransformer("all-MiniLM-L6-v2")
llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model_name="openai/gpt-oss-20b"
)


def create_chunks(pdf_path):

    text = read_pdf(pdf_path)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=50
    )

    return splitter.split_text(text)


def create_vector_store(pdf_path):

    chunks = create_chunks(pdf_path)

    embeddings = model.encode(chunks)

    embeddings = np.array(embeddings).astype("float32")

    index = faiss.IndexFlatL2(embeddings.shape[1])

    index.add(embeddings)

    return index, chunks


def search_document(question, index, chunks):

    question_embedding = model.encode([question])

    question_embedding = np.array(question_embedding).astype("float32")

    distance, result = index.search(question_embedding, k=4)

    retrieved_chunks = []

    for i in result[0]:
        retrieved_chunks.append(chunks[i])

    return retrieved_chunks
def ask_pdf(question, index, chunks):

    retrieved_chunks = search_document(question, index, chunks)

    context = "\n\n".join(retrieved_chunks)

    prompt = f"""
Answer the question only from the given context.

Context:
{context}

Question:
{question}
"""

    response = llm.invoke(prompt)

    return response.content