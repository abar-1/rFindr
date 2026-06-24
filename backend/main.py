from fastapi import FastAPI, APIRouter, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from db.SupabaseAPI import SupabaseAPI
from services.embeddingService import generate_Embedding
from api.authController import router as auth_router, get_current_user


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

# Auth routes: /api/auth/signup, /api/auth/login, /api/auth/logout, /api/auth/me
app.include_router(auth_router, prefix="/api")

class MatchRequest(BaseModel):
    interests: str
    num_matches: int

@app.post("/api/matches")
async def get_professor_matches(request: MatchRequest, current_user: dict = Depends(get_current_user)):
    try:
        user_id = current_user["id"]
        print(f"Received match request from user {user_id}:", request)

        # Identity comes from the auth cookie (current_user), not the request body,
        # so a client can't request matches on behalf of another user.
        print("Embedding generating...")
        embedding = generate_Embedding(request.interests)

        # Query Supabase for top professor matches
        matches = db.rag_Search(embedding, request.num_matches) or []

        print("Generated embedding:", embedding)
        print("matches =", matches)

        return matches

    except Exception as e:
        print("ERROR in /api/matches:", e)
        raise HTTPException(status_code=500, detail=str(e))
