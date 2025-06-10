# import openai
# from app.core.config import settings
# from app.services.vector_store import query_vector_store
# from app.crud import crud_item
# from sqlalchemy.ext.asyncio import AsyncSession
# # --- THIS IS THE KEY CHANGE ---
# from app.services.embedding_service import get_embedding

# openai.api_key = settings.OPENAI_API_KEY

# async def answer_question(db: AsyncSession, question: str):
#     """
#     The main RAG pipeline function.
#     """
#     print(f"Searching for context related to: '{question}'")
#     distances, retrieved_ids = query_vector_store(question, n_results=3)

#     if not retrieved_ids:
#         return "I'm sorry, I couldn't find any relevant information in the scraped data to answer your question."

#     context_str = ""
#     for item_id in retrieved_ids:
#         item = await crud_item.get(db, id=item_id)
#         if item:
#             context_str += f"Item Title: {item.title}\nDescription: {item.description}\nPrice: ${item.price}\nURL: {item.url}\n\n"

#     if not context_str:
#         return "I found some references, but couldn't retrieve their full details. Please try again."

#     prompt = f"""
#     You are a helpful assistant for an e-commerce website.
#     Answer the user's question based *only* on the context provided below.
#     If the context doesn't contain the answer, say that you don't have enough information.
#     Do not make up information.

#     Context:
#     ---
#     {context_str}
#     ---

#     User's Question: {question}

#     Answer:
#     """

#     print("--- PROMPT SENT TO OPENAI ---")
#     print(prompt)
#     print("----------------------------")

#     try:
#         # Use the new v1 API syntax for Chat Completion
#         response = openai.chat.completions.create(
#             model="gpt-3.5-turbo",
#             messages=[
#                 {"role": "system", "content": "You are a helpful assistant."},
#                 {"role": "user", "content": prompt}
#             ]
#         )
#         return response.choices[0].message.content.strip()
#     except Exception as e:
#         print(f"Error calling OpenAI API: {e}")
#         return "Sorry, there was an error processing your question with the AI model."

import openai
from app.core.config import settings
from app.services.vector_store import query_vector_store
from app.crud import crud_item
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.embedding_service import get_embedding

openai.api_key = settings.OPENAI_API_KEY

async def answer_question(db: AsyncSession, question: str):
    print(f"Searching for context related to: '{question}'")
    distances, retrieved_ids = query_vector_store(question, n_results=3)

    if not retrieved_ids:
        return "I'm sorry, I couldn't find any relevant information in the scraped data to answer your question."

    context_str = ""
    for item_id in retrieved_ids:
        # --- THIS IS THE CORRECTED LINE ---
        item = await crud_item.item.get(db, id=item_id)
        if item:
            context_str += f"Item Title: {item.title}\nDescription: {item.description}\nPrice: ${item.price}\nURL: {item.url}\n\n"

    if not context_str:
        return "I found some references, but couldn't retrieve their full details. Please try again."

    prompt = f"""
    You are a helpful assistant for an e-commerce website.
    Answer the user's question based *only* on the context provided below.
    If the context doesn't contain the answer, say that you don't have enough information.
    Do not make up information.

    Context:
    ---
    {context_str}
    ---

    User's Question: {question}

    Answer:
    """

    print("--- PROMPT SENT TO OPENAI ---")
    print(prompt)
    print("----------------------------")

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return "Sorry, there was an error processing your question with the AI model."