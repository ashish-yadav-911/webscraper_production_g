# from fastapi import APIRouter, Depends, Body
# from pydantic import BaseModel, HttpUrl
# from app.api import deps
# from app.models.user import User
# from scraper.tasks import scrape_website

# router = APIRouter()

# class ScrapeRequest(BaseModel):
#     url: HttpUrl

# @router.post("/scrape")
# def start_scraping(
#     scrape_in: ScrapeRequest,
#     current_user: User = Depends(deps.get_current_user)
# ):
#     """
#     Endpoint to start a new scraping job.
#     This is asynchronous. It returns immediately with a task ID.
#     """
#     task = scrape_website.delay(str(scrape_in.url), current_user.id)
#     return {"message": "Scraping job started", "task_id": task.id}

# app/api/endpoints/scraping.py

from fastapi import APIRouter, Depends, Body
from pydantic import HttpUrl # We only need HttpUrl now
from app.api import deps
# --- Import UserModel for type hinting ---
from app.models.user import User as UserModel
from scraper.tasks import scrape_website

router = APIRouter()

@router.post("/scrape")
def start_scraping(
    # --- This is the more robust way to define the expected body ---
    # It tells FastAPI to expect a JSON body like: {"url": "http://..."}
    url: HttpUrl = Body(..., embed=True),
    current_user: UserModel = Depends(deps.get_current_user)
):
    """
    Endpoint to start a new scraping job.
    This is asynchronous. It returns immediately with a task ID.
    """
    task = scrape_website.delay(str(url), current_user.id)
    return {"message": "Scraping job started", "task_id": task.id}