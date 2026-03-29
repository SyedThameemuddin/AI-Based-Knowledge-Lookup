import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from groq import Groq

import os

# 🔑 Set your Groq API key in environment variable GROQ_API_KEY
client = Groq(api_key=os.environ.get("GROQ_API_KEY", "your_groq_api_key_here"))

# Load embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')


# Load FAISS index
index = faiss.read_index("faiss_index.index")

# Load metadata
with open("metadata.pkl", "rb") as f:
    metadata = pickle.load(f)

texts = metadata["texts"]
shipment_ids = metadata["shipment_ids"]


def search(query, top_k=3):
    query_embedding = model.encode([query]).astype("float32")

    distances, indices = index.search(query_embedding, top_k)

    results = []
    for idx in indices[0]:
        results.append(texts[idx])

    return results


def generate_answer(query, context):
    prompt = f"""
You are a logistics assistant.
Answer strictly based on the context provided.

Context:
{context}

Question:
{query}
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


def main():
    print("RAG System Ready 🚀")

    while True:
        query = input("\nAsk a question (or type quit): ")

        if query.lower() == "quit":
            break

        results = search(query)
        context = "\n".join(results)

        answer = generate_answer(query, context)

        print("\nAnswer:\n", answer)


if __name__ == "__main__":
    main()
