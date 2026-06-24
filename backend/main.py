from fastapi import FastAPI, APIRouter, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from db.SupabaseAPI import SupabaseAPI
from services.embeddingService import generate_Embedding
from api.authController import router as auth_router, get_current_user
from api.ragController import router as rag_router


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
app.include_router(rag_router, prefix='/api')

