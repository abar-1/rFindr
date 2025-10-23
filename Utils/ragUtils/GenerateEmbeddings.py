from langchain.embeddings import HuggingFaceEmbeddings
import json

embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def generate_Embeddings(chunks: list[str]) -> list[list[float]]:
    embeddings = []
    for i in chunks:
        embeddings = generate_Embedding(i)
    return embeddings

def generate_Embedding(text: str) -> list[float]:
    embedding = embedding_model.embed_query(text)
    return embedding

def writeEmbeddingsToFile(embeddings: list[list[float]], file_path: str):
    with open(file_path, 'w') as f:
        json.dump(embeddings, f)



