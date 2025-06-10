import numpy as np
from sklearn.neighbors import NearestNeighbors
# --- THIS IS THE KEY CHANGE ---
from app.services.embedding_service import get_embedding
import joblib
import os
from typing import List, Tuple

# --- Configuration ---
VECTOR_STORE_DIR = "./vector_store_data"
NEIGHBORS_FILE = os.path.join(VECTOR_STORE_DIR, "neighbors_model.joblib")
VECTORS_FILE = os.path.join(VECTOR_STORE_DIR, "vectors.joblib")
IDS_FILE = os.path.join(VECTOR_STORE_DIR, "ids.joblib")
os.makedirs(VECTOR_STORE_DIR, exist_ok=True)

# --- In-memory cache ---
model: NearestNeighbors = None
vectors: List[np.ndarray] = []
ids: List[int] = []

def load_vector_store():
    """Loads the vector store from disk into memory."""
    global model, vectors, ids
    try:
        if os.path.exists(NEIGHBORS_FILE):
            model = joblib.load(NEIGHBORS_FILE)
            vectors = joblib.load(VECTORS_FILE)
            ids = joblib.load(IDS_FILE)
            print(f"Loaded vector store with {len(ids)} items.")
        else:
            print("No existing vector store found. Starting fresh.")
    except Exception as e:
        print(f"Could not load vector store, starting fresh. Error: {e}")
        model, vectors, ids = None, [], []

def add_item_to_vector_store(item_id: int, text: str):
    """Adds an item to the in-memory store and saves to disk."""
    global model, vectors, ids
    
    new_vector = get_embedding(text)
    
    vectors.append(new_vector)
    ids.append(item_id)
    
    if vectors:
        vectors_np = np.array(vectors)
        model = NearestNeighbors(n_neighbors=min(len(vectors), 5), algorithm='auto')
        model.fit(vectors_np)
    
    joblib.dump(model, NEIGHBORS_FILE)
    joblib.dump(vectors, VECTORS_FILE)
    joblib.dump(ids, IDS_FILE)
    
    print(f"Added item {item_id} and retrained vector store. Total items: {len(ids)}")

# def query_vector_store(query_text: str, n_results: int = 5) -> Tuple[list, list]:
#     """Queries the vector store for similar items."""
#     if model is None or not vectors:
#         return [], []
        
#     query_vector = np.array(get_embedding(query_text)).reshape(1, -1)
    
#     distances, indices = model.kneighbors(query_vector)
    
#     found_ids = [ids[i] for i in indices[0]]
    
#     return distances[0].tolist(), found_ids

# load_vector_store()

# In app/services/vector_store.py

def query_vector_store(query_text: str, n_results: int = 5) -> Tuple[list, list]:
    """Queries the vector store for similar items."""
    # --- THIS IS THE FIX ---
    # Load the latest data from the disk on every query.
    load_vector_store()
    
    if model is None or not vectors:
        return [], []
        
    query_vector = np.array(get_embedding(query_text)).reshape(1, -1)
    
    distances, indices = model.kneighbors(query_vector)
    
    found_ids = [ids[i] for i in indices[0]]
    
    return distances[0].tolist(), found_ids