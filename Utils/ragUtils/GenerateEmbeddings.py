from langchain.embeddings import HuggingFaceEmbeddings

embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def generate_Embeddings(chunks: list[str]) -> list[list[float]]:
    embeddings = embedding_model.embed_documents(chunks)
    return embeddings

def generate_Embedding(text: str) -> list[float]:
    embedding = embedding_model.embed_query(text)
    return embedding

