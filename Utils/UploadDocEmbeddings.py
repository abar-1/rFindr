import supabase
from ragUtils import GenerateEmbeddings
from ragUtils import ScrapeProfs
from ragUtils import DocumentChunker
import supabase
import json
from supabase import create_client, Client
import os
print("imports done")
DATABASE_URL = os.getenv("DATABASE_URL")
SUPABASE_PUBLIC = os.getenv("SUPABASE_PUBLIC")

VDB_API_URL = DATABASE_URL
VDB_ANON_KEY = SUPABASE_PUBLIC

docChunker = DocumentChunker.DocumentChunker(chunk_token_size=500, overlap=100)


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
        response = (
            client.table('professor_embeddings')
            .insert(JSON_data.embeddings)
            .execute()
        )

        if response.data:
            print("Successfully uploaded embeddings to VDB.")
        else:
            print("Failed to upload embeddings to VDB.")
    
    except Exception as e:
        print(f"Error uploading embeddings: {e}")

def chunkPlainText(plainText: str) -> list[str]:
    return docChunker.chunk_text(plainText)

def chunkDocuments(docPaths: list[str]) -> list[str]:
    return docChunker.chunk_documents_paragraphs(docPaths)

'''Program Starts Here'''

#docPaths = []
url = "https://www.cs.purdue.edu/people/faculty/aliaga.html"
name, email, details = ScrapeProfs.get_professor_info(url)
print(f"Scraped professor: {name}, Email: {email}")

chunks = []
#chunks = chunkDocuments(docPaths)
#chunks = chunkPlainText(details)

embeddings = GenerateEmbeddings.generate_Embedding(details)
print(f"Generated {len(embeddings)} embeddings for professor {name}.")

# for chunk, embedding in zip(chunks, embeddings):
#     uploadEmbeddingToVDB(makeJSONPayload(name = name,email=email, embeddings=embeddings))

uploadEmbeddingToVDB(makeJSONPayload(name = name,email=email, embeddings=embeddings))

 

