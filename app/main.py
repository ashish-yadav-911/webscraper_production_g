# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware

# from app.api.endpoints import users, scraping, query
# from app.db.session import engine, Base

# # This function will be called at startup to create DB tables
# async def create_db_and_tables():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)

# app = FastAPI(title="Production Grade Scraper API")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Allows all origins
#     allow_credentials=True,
#     allow_methods=["*"],  # Allows all methods
#     allow_headers=["*"],  # Allows all headers
# )


# @app.on_event("startup")
# async def on_startup():
#     await create_db_and_tables()

# # Include routers
# api_prefix = "/api/v1"
# app.include_router(users.router, prefix=f"{api_prefix}/users", tags=["users"])
# app.include_router(scraping.router, prefix=f"{api_prefix}/scraping", tags=["scraping"])
# app.include_router(query.router, prefix=f"{api_prefix}/query", tags=["query"])

# @app.get("/")
# def read_root():
#     return {"message": "Welcome to the Scraper API. Go to /docs to see the endpoints."}





# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from app.api.endpoints import users, scraping, query
from app.db.session import engine, Base
import os

# Create the main application
app = FastAPI(title="Production Grade Scraper API")

# --- Middleware (CORS) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Routers ---
api_prefix = "/api/v1"
app.include_router(users.router, prefix=f"{api_prefix}/users", tags=["users"])
app.include_router(scraping.router, prefix=f"{api_prefix}/scraping", tags=["scraping"])
app.include_router(query.router, prefix=f"{api_prefix}/query", tags=["query"])

# --- Frontend Serving ---

# 1. Mount the 'static' directory to serve CSS and JS files
# This makes files in the 'static' folder available under '/static'
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# 2. Serve the main index.html file for the root URL
@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open(os.path.join(static_dir, "index.html")) as f:
        return HTMLResponse(content=f.read(), status_code=200)

# --- Database Initialization ---
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)