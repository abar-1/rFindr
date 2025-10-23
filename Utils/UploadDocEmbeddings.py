from Utils.ragUtils import ScrapeProfs
from ragUtils import DocumentChunker, GenerateEmbeddings
import supabase
import json
from supabase import create_client, Client

VDB_API_URL = ""
VDB_ANON_KEY = ""

docChunker = DocumentChunker.DocumentChunker(chunk_token_size=500, overlap=100)
embedGenerator = GenerateEmbeddings.EmbeddingGenerator()

def makeJSONPayload(name : str, email: str, embeddings: list[float]) -> dict:
    profName = name
    profEmail = email
    profEmbeddings = embeddings

    payload = {
        "name": profName,
        "email": profEmail,
        "embeddings": profEmbeddings
    }

    return payload

def uploadEmbeddingToVDB(JSONPayload: dict):
    client = create_client(VDB_API_URL, VDB_ANON_KEY)
    JSON_data = [JSONPayload]
    try:
        JSON_data = json.dumps(JSON_data, ensure_ascii=False, indent=2)
        #Edit this to match VDB structure
        client.storage.from_('embeddings').upload(
            path = 'embeddings.json', 
            file = JSON_data.encode('utf-8'),
            file_options={"content-type": "application/json"}            
            )
        
        print("Successfully uploaded embeddings to VDB.")
    
    except Exception as e:
        print(f"Error uploading embeddings: {e}")

def chunkPlainText(plainText: str) -> list[str]:
    return docChunker.chunk_text(plainText)

def chunkDocuments(docPaths: list[str]) -> list[str]:
    return docChunker.chunk_documents_paragraphs(docPaths)

'''Program Starts Here'''

#docPaths = []
url = ''
name, email, details = ScrapeProfs.get_professor_info(url)

chunks = []
#chunks = chunkDocuments(docPaths)
chunks = chunkPlainText(details)

embeddings = embedGenerator.generate_Embeddings(chunks)

for chunk, embedding in zip(chunks, embeddings):
    uploadEmbeddingToVDB(makeJSONPayload(name = name,email=email, embeddings=embeddings))

 

