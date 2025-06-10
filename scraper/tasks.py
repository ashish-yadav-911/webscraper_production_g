import httpx
from app.db.session import SessionLocal
from app.crud import crud_item
from app.schemas.item import ItemCreate
from app.services.vector_store import add_item_to_vector_store
from app.services.embedding_service import get_embedding
from celery_worker import celery_app
import asyncio
from app.models.user import User
from scraper.parsers import get_parser

@celery_app.task
def scrape_website(url: str, user_id: int):
    """
    The Celery task that performs the scraping.
    """
    print(f"Starting scrape for URL: {url} for user_id: {user_id}")
    try:
        with httpx.Client() as client:
            response = client.get(url, follow_redirects=True, timeout=20.0)
            response.raise_for_status()
            html_content = response.text

        # --- THIS IS THE FIXED LINE ---
        parser = get_parser(url, html_content)

        parsed_items = parser.parse(html_content, url)
        print(f"Parsed {len(parsed_items)} items from {url}")

        async def save_items():
            async with SessionLocal() as db:
                for item_data in parsed_items:
                    db_item = await crud_item.item.create_with_owner(
                        db=db, obj_in=ItemCreate(**item_data), owner_id=user_id
                    )
                    await db.flush() 
                    text_for_embedding = f"Title: {db_item.title}. Description: {db_item.description}"
                    add_item_to_vector_store(item_id=db_item.id, text=text_for_embedding)
                
                await db.commit()

        asyncio.run(save_items())
        return {"status": "success", "url": url, "items_found": len(parsed_items)}
    except Exception as e:
        print(f"Scraping failed for {url}. Detailed Error: {e}")
        return {"status": "failed", "url": url, "error": str(e)}