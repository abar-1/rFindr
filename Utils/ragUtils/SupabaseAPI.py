import os
from supabase import create_client, Client
from ragUtils import GenerateEmbeddings, ScrapeProfs, DocumentChunker
from dotenv import load_dotenv

class SupabaseAPI:
    supabase: Client
    profNames: list[str]

    def __init__(self):
        self.__setup_Supabase()

    def __main__(self, case: int = 0):
        if case == 1:
            ud = SupabaseAPI()

            url = "https://www.cs.purdue.edu/people/faculty/aliaga.html"
            ud.upload_embedding(url)
        else:
            return "case = 0, set case = 1 to run example."
    
# ============ UPLOAD EMBEDDINGS TO DB ============= #
    def upload_embedding(self, url: str):
        self.__get_Prof_Names()
        if not url:
            raise ValueError("URL must be provided.")
        
        name, email, details = ScrapeProfs.get_professor_info(url)
        embedding = GenerateEmbeddings.generate_Embedding(details)
        print(f"Generated embedding for professor {name}.")

        if name in self.profNames:
            print(f"Professor {name} already exists in the database. Skipping upload.")
            return
        prof_id = self.__upsert_professor(name=name, email=email, research_areas=details)
        self.__insert_professor_embedding(professor_id=prof_id, embedding=embedding, chunk=details)
        print(f"Successfully uploaded embeddings to VDB for prof: {name}.")

    
        
    def __setup_Supabase(self)-> None:
        load_dotenv()
        SUPABASE_URL = os.getenv("DATABASE_URL")
        SUPABASE_ANON_KEY = os.getenv("SUPABASE_PUBLIC")

        if not SUPABASE_URL or not SUPABASE_ANON_KEY:
            raise RuntimeError("Set SUPABASE_URL and SUPABASE_ANON_KEY in your environment.")
        
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        docChunker = DocumentChunker.DocumentChunker(chunk_token_size=500, overlap=100)


    def __upsert_professor(self, name: str, email: str, department: str | None = None, research_areas: str | None = None) -> int:
        payload = {"name": name, "email": email}
        if department is not None:
            payload["department"] = department
        if research_areas is not None:
            payload["research_areas"] = research_areas
        self.supabase.table("professors").upsert(payload, on_conflict="email").execute()
        resp = self.supabase.table("professors").select("id").eq("email", email).single().execute()
        return resp.data["id"]

    def __insert_professor_embedding(self, professor_id: int, embedding: list[float], chunk: str) -> None:
        self.supabase.table("professor_embeddings").insert({"professor_id": professor_id, "embedding": embedding, "chunk": chunk}).execute()

# ============ Get Data From DB ============= #
    def __get_Prof_Names(self) -> None:
        resp = self.supabase.table("professors").select("name").execute()
        self.profNames = [record["name"] for record in resp.data]

    def rag_Search (self, query: str, match_count: int = 5) -> list[dict]:
        embedding = GenerateEmbeddings.generate_Embedding(query)
        resp = self.supabase.rpc("match_professor_embeddings", {"query_embedding": embedding, "match_count": match_count}).execute()
        return resp.data

    
if __name__ == "__main__":
    uploadProfs = SupabaseAPI()
    uploadProfs.reset_prof_id_numeration()



    