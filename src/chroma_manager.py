import os
import logging
from typing import List, Dict, Any
import chromadb
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
load_dotenv()


class ChromaManager:
    """
    Handles ChromaDB ingestion and storage.
    """
    def __init__(self, collection_name: str = None, persist_path: str = "chroma"):
        self.collection_name = collection_name or os.environ.get('CHROMA_COLLECTION_NAME')
        self.persist_path = persist_path
        self.chroma_client = chromadb.PersistentClient(path=self.persist_path)

    def get_or_create_collection(self):
        try:
            return self.chroma_client.get_collection(self.collection_name)
        except Exception:
            logging.info(f"Creating new Chroma collection: {self.collection_name}")
            return self.chroma_client.create_collection(name=self.collection_name)

    def ingest(self, chunks: List[str], metadatas: List[Dict[str, Any]], embeddings: List[List[float]]):
        """
        Store everything in Chroma collection.
        """
        collection = self.get_or_create_collection()
        ids = [str(i) for i in range(len(chunks))]
        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas
        )
        logging.info(f"Added {len(chunks)} chunks to Chroma collection '{self.collection_name}'")
        return collection
    
    def query(self, embeddings, n_results: int = 10):
        collection = self.get_or_create_collection()
        results = collection.query(
            query_embeddings=embeddings,
            n_results=n_results,              
            include=['documents', 'metadatas', 'distances'] 
        )

        search_results = ""
        for i, doc in enumerate(results['documents'][0]):
            content = f"<Rank {i+1}>\n{doc}\n</Rank {i+1}\n>"
            search_results += content
        return search_results
