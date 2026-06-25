import os
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel

from api.authController import get_current_user
from services.embeddingService import generate_Embedding

from db.SupabaseAPI import SupabaseAPI

router = APIRouter(prefix="/rag", tags=["rag"])
db = SupabaseAPI()

class MatchRequest(BaseModel):
    interests: str
    num_matches: int

class ChatRequest(BaseModel):
    matches: list[dict]
    interests: str

@router.post("/matches", status_code=status.HTTP_200_OK)
def get_matches(request: MatchRequest, current_user: dict = Depends(get_current_user)):
    try:
        user_id = current_user["id"]
        
        embedding = generate_Embedding(request.interests)
        
        #validation check 
        if not embedding:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Embedding service returned an empty response."
            )

        matches = db.rag_Search(embedding, request.num_matches) or []
        return matches

    except HTTPException:
        # Crucial: allows any HTTPException we manually raised above to pass through untouched
        raise
    except Exception as e:
        # Catch-all for database failures or unexpected runtime bugs
        print(f"Database or system error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal server error occurred."
        )

@router.post("/save", status_code=status.HTTP_201_CREATED)
def save_chat_log(request: ChatRequest, current_user: dict = Depends(get_current_user)):
    try:
        user_id = current_user["id"]

        query = request.interests.strip()
        if not query:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="interests must be a non-empty string.",
            )

        if not request.matches:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="matches must contain at least one result.",
            )

        saved = db.insert_chat(user_id, query, request.matches)
        return {"id": saved["id"], "saved": True}

    except HTTPException:
        # Let our own validation errors pass through untouched.
        raise
    except Exception as e:
        # DB failures or unexpected runtime bugs become a 500, never a silent success.
        print(f"Failed to save chat log: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save chat log.",
        )
@router.get("/chats", status_code=status.HTTP_200_OK)
def get_chats(current_user: dict = Depends(get_current_user)):
    try:
        user_id = current_user["id"]

        chats = db.get_chats_by_user(user_id)
        return chats
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server failed to get chat logs"
        )