from ragUtils import DocumentChunker, GenerateEmbeddings

docChunker = DocumentChunker.DocumentChunker(chunk_token_size=500, overlap=50)
embedGenerator = GenerateEmbeddings.EmbeddingGenerator()

VDB_API_URL = ""

docPaths = []
plainText = ""

chunks = []#Chunk Docs or plain text
embeddings = embedGenerator.generate_Embeddings(chunks)

#upload embeddings to VDB


def chunkPlainText(plainText: str) -> list[str]:
    return docChunker.chunk_text(plainText)

def chunkDocuments(docPaths: list[str]) -> list[str]:
    return docChunker.chunk_documents(docPaths)


def uploadEmbeddingsToVDB(embeddings: list[list[float]], VDB_API_URL: str):
    pass  




