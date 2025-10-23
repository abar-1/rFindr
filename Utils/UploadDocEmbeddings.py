import os
from supabase import create_client, Client
from ragUtils import GenerateEmbeddings, ScrapeProfs, DocumentChunker
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("DATABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_PUBLIC")

if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    raise RuntimeError("Set SUPABASE_URL and SUPABASE_ANON_KEY in your environment.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

docChunker = DocumentChunker.DocumentChunker(chunk_token_size=500, overlap=100)
print("imports done")

def upsert_professor(name: str, email: str, department: str | None = None, research_areas: str | None = None) -> int:
    payload = {"name": name, "email": email}
    if department is not None:
        payload["department"] = department
    if research_areas is not None:
        payload["research_areas"] = research_areas
    supabase.table("professors").upsert(payload, on_conflict="email").execute()
    resp = supabase.table("professors").select("id").eq("email", email).single().execute()
    return resp.data["id"]

def insert_professor_embedding(professor_id: int, embedding: list[float]):
    supabase.table("professor_embeddings").insert({"professor_id": professor_id, "embedding": embedding}).execute()

#---Program Start---#
url = "https://www.cs.purdue.edu/people/faculty/aliaga.html"
name, email, details = ScrapeProfs.get_professor_info(url)
print(f"Scraped professor: {name}, Email: {email}")

embedding = GenerateEmbeddings.generate_Embedding(details)
print(f"Generated {len(embedding)}-dim embedding for professor {name}.")

prof_id = upsert_professor(name=name, email=email, research_areas=details)
insert_professor_embedding(professor_id=prof_id, embedding=embedding)
print("Successfully uploaded embeddings to VDB.")