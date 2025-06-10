# import httpx
# from sqlalchemy.orm import sessionmaker
# from app.db.session import engine
# from app.crud import crud_item
# from app.schemas.item import ItemCreate
# from app.services.vector_store import add_item_to_vector_store
# from scraper.parsers import get_parser
# from celery_worker import celery_app

# # Create a new session for the celery worker, as it runs in a separate process
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# @celery_app.task
# def scrape_website(url: str, user_id: int):
#     """
#     The Celery task that performs the scraping.
#     """
#     print(f"Starting scrape for URL: {url} for user_id: {user_id}")
#     try:
#         # 1. Get correct parser for the URL
#         parser = get_parser(url)

#         # 2. Fetch the HTML content asynchronously
#         with httpx.Client() as client:
#             response = client.get(url, follow_redirects=True, timeout=20.0)
#             response.raise_for_status() # Raise exception for 4xx/5xx status codes
#             html_content = response.text

#         # 3. Parse the content
#         parsed_items = parser.parse(html_content)
#         print(f"Parsed {len(parsed_items)} items from {url}")

#         # 4. Save to database and vector store
#         # IMPORTANT: Celery tasks must manage their own DB sessions
#         async def save_items():
#             async with SessionLocal() as db:
#                 for item_data in parsed_items:
#                     item_schema = ItemCreate(**item_data)
#                     # Save to relational DB
#                     db_item = await crud_item.create_with_owner(
#                         db=db, obj_in=item_schema, owner_id=user_id
#                     )
#                     # Add to vector store for RAG
#                     text_for_embedding = f"Title: {db_item.title}. Description: {db_item.description}"
#                     add_item_to_vector_store(item_id=db_item.id, text=text_for_embedding)

#         # Since this is a sync celery task, we run the async part like this
#         import asyncio
#         asyncio.run(save_items())
        
#         return {"status": "success", "url": url, "items_found": len(parsed_items)}

#     except Exception as e:
#         print(f"Scraping failed for {url}. Error: {e}")
#         # You can add more robust error handling here, like retrying the task
#         return {"status": "failed", "url": url, "error": str(e)}
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
    print(f"Starting scrape for URL: {url} for user_id: {user_id}")
    try:
        parser = get_parser(url)
        with httpx.Client() as client:
            response = client.get(url, follow_redirects=True, timeout=20.0)
            response.raise_for_status()
            html_content = response.text
        parsed_items = parser.parse(html_content)
        print(f"Parsed {len(parsed_items)} items from {url}")

        async def save_items():
            async with SessionLocal() as db:
                for item_data in parsed_items:
                    db_item = await crud_item.item.create_with_owner(
                        db=db, obj_in=ItemCreate(**item_data), owner_id=user_id
                    )
                    # We must flush to get the ID for the vector store
                    await db.flush() 
                    text_for_embedding = f"Title: {db_item.title}. Description: {db_item.description}"
                    add_item_to_vector_store(item_id=db_item.id, text=text_for_embedding)
                
                # --- THIS IS THE CRITICAL FIX ---
                # The commit must happen INSIDE the 'with' block,
                # before the session is closed.
                await db.commit()

        asyncio.run(save_items())
        return {"status": "success", "url": url, "items_found": len(parsed_items)}
    except Exception as e:
        print(f"Scraping failed for {url}. Detailed Error: {e}")
        return {"status": "failed", "url": url, "error": str(e)}