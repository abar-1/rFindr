from ragUtils import DocumentChunker, GenerateEmbeddings, WebScrapper
import supabase
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

def uploadEmbeddingsToVDB(embeddings: list[list[float]]):
    client = create_client(VDB_API_URL, VDB_ANON_KEY)
    try:
        client.storage.from_('embeddings').upload('embeddings.json', embeddings)
        print("Successfully uploaded embeddings to VDB.")
    except Exception as e:
        print(f"Error uploading embeddings: {e}")
    

docPaths = []
plainText = ""

chunks = []

chunks = chunkDocuments(docPaths)
#chunks = chunkPlainText(plainText)

embeddings = embedGenerator.generate_Embeddings(chunks)
uploadEmbeddingsToVDB(embeddings)


 

