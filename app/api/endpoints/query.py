from typing import List
from fastapi import APIRouter, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.models.user import User
from app.services import rag_service
from app.crud import crud_item
from app.schemas.item import Item as ItemSchema
from app.models.user import User as UserModel

router = APIRouter()

@router.get("/all-items", response_model=List[ItemSchema])
async def read_all_scraped_items(
    db: AsyncSession = Depends(deps.get_db),
    current_user: UserModel = Depends(deps.get_current_user),
):
    """
    Retrieve all items scraped by the current user.
    """
    items = await crud_item.item.get_multi_by_owner(db=db, owner_id=current_user.id)
    return items

@router.post("/query")
async def ask_question(
    question: str = Body(..., embed=True),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user) # Ensures only logged-in users can query
):
    """
    Endpoint for the RAG system. Ask a question about the scraped data.
    """
    answer = await rag_service.answer_question(db=db, question=question)
    return {"question": question, "answer": answer}