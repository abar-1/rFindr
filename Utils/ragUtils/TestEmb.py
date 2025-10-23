from sentence_transformers import SentenceTransformer

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device="cpu")  # force CPU first
emb = model.encode("This is a sample text for generating embeddings.", normalize_embeddings=True)
print(len(emb), emb[:5])