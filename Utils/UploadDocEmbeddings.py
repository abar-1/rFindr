from ragUtils import DocumentChunker, GenerateEmbeddings, WebScrapper
import supabase
import json
from supabase import create_client, Client

VDB_API_URL = ""
VDB_ANON_KEY = ""

docChunker = DocumentChunker.DocumentChunker(chunk_token_size=500, overlap=100)
embedGenerator = GenerateEmbeddings.EmbeddingGenerator()
webScrape = WebScrapper.WebScraper()

def getTextFromURL(url: str) -> str:
    return webScrape.scrape_webpage(url)

def chunkPlainText(plainText: str) -> list[str]:
    return docChunker.chunk_text(plainText)

def chunkDocuments(docPaths: list[str]) -> list[str]:
    return docChunker.chunk_documents_paragraphs(docPaths)

def uploadEmbeddingToVDB(embedding: list[float], chunk: str = ""):
    client = create_client(VDB_API_URL, VDB_ANON_KEY)
    JSON_data = [{"chunk": chunk, "embedding": embedding}]
    try:
        JSON_data = json.dumps(JSON_data, ensure_ascii=False, indent=2)

        client.storage.from_('embeddings').upload(
            path = 'embeddings.json', 
            file = JSON_data.encode('utf-8'),
            file_options={"content-type": "application/json"}            
            )
        
        print("Successfully uploaded embeddings to VDB.")
    
    except Exception as e:
        print(f"Error uploading embeddings: {e}")
    

docPaths = []
plainText = ""

chunks = []

chunks = chunkDocuments(docPaths)
#chunks = chunkPlainText(plainText)

embeddings = embedGenerator.generate_Embeddings(chunks)
for chunk, embedding in zip(chunks, embeddings):
    uploadEmbeddingToVDB(embedding, chunk)


 

