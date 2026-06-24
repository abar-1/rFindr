import os
from supabase import create_client, Client
import services.embeddingService as embeddingService
from services.embeddingService import generate_Embedding
from services.ScrapeProfs import scrape_professor_page, get_professor_info
from services.docChunkerService import DocumentChunker
from dotenv import load_dotenv
from typing import Optional
import os, json, requests

class SupabaseAPI:
    supabase: Client
    profNames: list[str]

    def __init__(self):
        self.__setup_Supabase()

    def __main__(self):
        pass
    
# ============ UPLOAD EMBEDDINGS TO DB ============= #
# Uses Supabase client to upload info to the database
    def upload_prof_embedding(self, url: str):
        self.__get_Prof_Names()
        if not url:
            raise ValueError("URL must be provided.")
        
        name, email, details = get_professor_info(url)
        # get_professor_info may return several emails joined by "; "; keep the first usable one.
        email = email.split(";")[0].strip() if email and email != "N/A" else None
        embedding = embeddingService.generate_Embedding(details)
        print(f"Generated embedding for professor {name}.")

        if name in self.profNames:
            print(f"Professor {name} already exists in the database. Skipping upload.")
            return
        prof_id = self.__upsert_professor(name=name, email=email, research_areas=details)
        self.__insert_professor_embedding(professor_id=prof_id, embedding=embedding, chunk=details)
        print(f"Successfully uploaded embeddings to VDB for prof: {name}.")
        
    def upload_user_embedding(self, user_id: int, user_bio: str):
        embedding = embeddingService.generate_Embedding(user_bio)
        print(f"Generated embedding for user ID {user_id}.")
        self.__insert_user_enbedding(user_id=user_id, embedding=embedding)
        print(f"Successfully uploaded user embedding to VDB for user ID: {user_id}.")
        
    def __setup_Supabase(self) -> None:
        load_dotenv()
        SUPABASE_URL = os.getenv("DATABASE_URL")
        SUPABASE_ANON_KEY = os.getenv("SUPABASE_PUBLIC")

        if not SUPABASE_URL or not SUPABASE_ANON_KEY:
            raise RuntimeError("Set SUPABASE_URL and SUPABASE_ANON_KEY in your environment.")
        
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        docChunker = DocumentChunker(chunk_token_size=500, overlap=100)


    def __upsert_professor(self, name: str, email: Optional[str] = None, research_areas: Optional[str] = None, department: Optional[str] = None) -> int:
        payload = {"name": name}
        if department is not None:
            payload["department"] = department
        if research_areas is not None:
            payload["research_areas"] = research_areas

        # Only dedupe on email when we actually have one; the column is UNIQUE and
        # the .single() lookup below breaks if many rows share a placeholder email.
        if email:
            payload["email"] = email
            self.supabase.table("professors").upsert(payload, on_conflict="email").execute()
            resp = self.supabase.table("professors").select("id").eq("email", email).single().execute()
            return resp.data["id"]

        resp = self.supabase.table("professors").insert(payload).execute()
        return resp.data[0]["id"]

    def __insert_professor_embedding(self, professor_id: int, embedding: list[float], chunk: str) -> None:
        self.supabase.table("professor_embeddings").insert({"professor_id": professor_id, "embedding": embedding, "chunk": chunk}).execute()

    def __insert_user_enbedding(self, user_id: int, embedding: list[float]) -> None:
        self.supabase.table("user_embeddings").insert({"user_id": user_id, "embedding": 
        embedding}).execute()

# ============ Get Data From DB ============= #
# Uses Request to call Supabase functions
    def rag_Search(self, embedding: list[float], match_count: int = 5) -> list[dict]:
        results = self.__get_DB_Vectors(embedding)
        if len(results) < match_count:
            return results
        return results[:match_count]
    
    def __get_DB_Vectors(self, embedding: list[float]) -> list[dict]:
        load_dotenv()
        SUPABASE_URL = os.getenv("DATABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_PUBLIC")

        endpoint = f"{SUPABASE_URL}/rest/v1/rpc/top_professor_matches" #top_professor_matches = function name in supabase

        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        payload = {
            "user_embedding": [float(x) for x in embedding]
        }

        r = requests.post(endpoint, headers=headers, data=json.dumps(payload)) #use requests to post data to supabase function

        data = r.json()
        return data
    
    def __get_Num_Embeddings(self) -> int:
        url = os.getenv("DATABASE_URL")  
        key = os.getenv("SUPABASE_PUBLIC")
        r = requests.post(
            f"{url}/rest/v1/rpc/debug_count_embeddings",
            headers={
                "apikey": key,
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            data=json.dumps({})  # no args
        )

        print("status", r.status_code)
        print("body", r.text)


    def __get_Prof_Names(self) -> None:
        resp = self.supabase.table("professors").select("name").execute()
        self.profNames = [record["name"] for record in resp.data]

    
if __name__ == "__main__":
    db = SupabaseAPI()

    

    