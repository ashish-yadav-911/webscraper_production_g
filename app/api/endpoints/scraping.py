# app/api/endpoints/scraping.py

from fastapi import APIRouter, Depends, Body
from pydantic import HttpUrl
from celery.result import AsyncResult
from app.api import deps
from app.models.user import User as UserModel
from scraper.tasks import scrape_website
from celery_worker import celery_app
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud import crud_item

router = APIRouter()

@router.post("/scrape")
def start_scraping(
    url: HttpUrl = Body(..., embed=True),
    current_user: UserModel = Depends(deps.get_current_user)
):
    task = scrape_website.delay(str(url), current_user.id)
    return {"message": "Scraping job started", "task_id": task.id}

# --- THIS IS THE NEW POLLING ENDPOINT ---
@router.get("/scrape/status/{task_id}")
async def get_scrape_status(
    task_id: str,
    db: AsyncSession = Depends(deps.get_db),
    current_user: UserModel = Depends(deps.get_current_user)
):
    """
    Checks the status of a Celery task. If successful, it fetches the scraped data.
    """
    task_result = AsyncResult(task_id, app=celery_app)
    
    if task_result.failed():
        return {"status": "failed", "error": str(task_result.result)}

    if not task_result.ready():
        return {"status": "pending"}

    # Task succeeded, now fetch the data
    scraped_data = await crud_item.item.get_multi_by_owner(db, owner_id=current_user.id)
    return {"status": "success", "data": scraped_data}







# from fastapi import APIRouter, Depends, Body
# from pydantic import HttpUrl # We only need HttpUrl now
# from app.api import deps
# # --- Import UserModel for type hinting ---
# from app.models.user import User as UserModel
# from scraper.tasks import scrape_website

# router = APIRouter()

# @router.post("/scrape")
# def start_scraping(
#     # --- This is the more robust way to define the expected body ---
#     # It tells FastAPI to expect a JSON body like: {"url": "http://..."}
#     url: HttpUrl = Body(..., embed=True),
#     current_user: UserModel = Depends(deps.get_current_user)
# ):
#     """
#     Endpoint to start a new scraping job.
#     This is asynchronous. It returns immediately with a task ID.
#     """
#     task = scrape_website.delay(str(url), current_user.id)
#     return {"message": "Scraping job started", "task_id": task.id}