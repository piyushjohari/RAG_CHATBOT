"""
Run on command prompt
"""

from dotenv import load_dotenv
from src.llm_calls import get_llm_answer
from src.chroma_manager import ChromaManager
from src.embeddings import Embedder

load_dotenv()
embedder = Embedder()
chroma_manager = ChromaManager()

choice = True
while choice:
    query_text = input("Your Query: ")
    embeddings = embedder.embed_user_query(query_text)
    search_results = chroma_manager.query(embeddings)
    answer = get_llm_answer(query_text, search_results)
    print("ANSWER", answer)