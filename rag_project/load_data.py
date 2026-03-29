import pandas as pd
import numpy as np
import faiss
import pickle
from sentence_transformers import SentenceTransformer

# Load embedding model (384 dimensions)
model = SentenceTransformer('all-MiniLM-L6-v2')

def load_excel(file_path):
    df = pd.read_excel(file_path)
    texts = []
    shipment_ids = []

    for _, row in df.iterrows():
        content = ". ".join([f"{col}: {row[col]}" for col in df.columns if pd.notna(row[col])])
        texts.append(content)
        shipment_ids.append(str(row['shipment_id']))

    return texts, shipment_ids


def main():
    print("Reading Excel file...")
    texts, shipment_ids = load_excel("shipments.xlsx")

    print("Generating embeddings...")
    embeddings = model.encode(texts)

    # Convert to numpy float32
    embeddings = np.array(embeddings).astype("float32")

    dimension = embeddings.shape[1]

    print("Creating FAISS index...")
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    # Save index
    faiss.write_index(index, "faiss_index.index")

    # Save metadata
    with open("metadata.pkl", "wb") as f:
        pickle.dump({"texts": texts, "shipment_ids": shipment_ids}, f)

    print("Data successfully indexed and saved!")

if __name__ == "__main__":
    main()
