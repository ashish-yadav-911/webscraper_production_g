import openai
import numpy as np
from app.core.config import settings

openai.api_key = settings.OPENAI_API_KEY

def get_embedding(text: str, model="text-embedding-ada-002") -> np.ndarray:
   """Generates an embedding for a given text using OpenAI."""
   text = text.replace("\n", " ")
   # Use the new v1 API syntax for creating embeddings
   response = openai.embeddings.create(input=[text], model=model)
   return response.data[0].embedding