from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from Utils.SupabaseAPI import SupabaseAPI
from Utils.ragUtils import EmbGenerator

app = FastAPI()
router = APIRouter()
db = SupabaseAPI()

# Allow the frontend (Next.js dev) to call the API during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MatchRequest(BaseModel):
    interests: str
    user_id: int
    num_matches: int

@app.post("/api/matches")
async def get_professor_matches(request: MatchRequest):
    try:
        print("Received match request:", request)

        # Generate embedding for the user's interests if it doesn't exist
        #add logic to check if user after adding user auth, for now assume user doesn't have existing embedding
        print("Embedding generating...")
        embedding = EmbGenerator.generate_Embedding(request.interests)

        # Query Supabase for top professor matches
        matches = db.rag_Search(embedding, request.num_matches) or []

        print("Generated embedding:", embedding)
        print("matches =", matches)

        return matches

    except Exception as e:
        print("ERROR in /api/matches:", e)
        raise HTTPException(status_code=500, detail=str(e))
