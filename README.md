# webscraper_production_g
# AI Production-Grade Scraper

This project is a complete, scalable web scraping platform built with a modern Python backend and a dynamic vanilla JavaScript frontend. It allows users to register, log in, submit scraping jobs for various websites, and ask natural language questions about the scraped data using a Retrieval-Augmented Generation (RAG) system.

## Features

- **Backend:** FastAPI (Asynchronous, High-Performance)
- **Asynchronous Scraping:** Celery with Redis for background job processing.
- **Data Storage:**
    - **Relational:** SQLAlchemy with SQLite for structured data (titles, prices, etc.).
    - **Vector:** Scikit-learn & Joblib for a robust, file-based vector store for RAG.
- **Authentication:** JWT (JSON Web Tokens) for secure user management.
- **RAG System:** OpenAI's models (`text-embedding-ada-002`, `gpt-3.5-turbo`) for semantic search and Q&A.
- **Multi-Strategy Parsing:** Uses the Strategy Design Pattern to support multiple website layouts (e.g., specific parsers for e-commerce and a generic fallback for simple text sites).
- **Frontend:** Clean, modern UI built with vanilla HTML, CSS, and JavaScript. No frameworks required. Served directly from the FastAPI backend.

---

## Setup and Installation

### Prerequisites

- Python 3.11+
- Redis (can be run easily with Docker: `docker run -d -p 6379:6379 redis`)

### 1. Project Setup

Clone this repository or create the directory structure as laid out in the files.

### 2. Virtual Environment

It is highly recommended to use a virtual environment.

```bash
# Navigate to the project root
cd production_scraper

# Create a virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate