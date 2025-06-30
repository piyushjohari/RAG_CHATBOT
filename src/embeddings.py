import os
import json
import csv
import logging
from typing import List
from openai import OpenAI
from dotenv import load_dotenv
from src.chroma_manager import ChromaManager
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
load_dotenv()

class Embedder:
    """
    Handles text chunking, embedding, and metadata creation.
    """
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None, embed_model: str = None):
        self.chunk_size = int(chunk_size or os.environ.get('PDF_CHUNK_SIZE', 1000))
        self.chunk_overlap = int(chunk_overlap or os.environ.get('PDF_CHUNK_OVERLAP', 150))
        self.embed_model = embed_model or os.environ.get('EMBED_MODEL')
        self.client = OpenAI()

    def chunk_text(self, text: str, filename: str = "") -> List[str]:
        """Chunk long text with overlap."""
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            chunk = f'{filename} {text[start:end]}'
            chunks.append(chunk)
            if end == len(text):
                break
            start += self.chunk_size - self.chunk_overlap
        return chunks

    def process_text_folder(self, folder: str):
        """Process all .txt files in a folder."""
        all_chunks, all_metadata = [], []
        for fname in os.listdir(folder):
            if fname.lower().endswith('.txt'):
                fpath = os.path.join(folder, fname)
                with open(fpath, 'r', encoding='utf-8') as f:
                    pdf_text = f.read()
                chunks = self.chunk_text(pdf_text, fname)
                meta = [{"source": "text", "chunk_id": i, "file": fname} for i in range(len(chunks))]
                all_chunks.extend(chunks)
                all_metadata.extend(meta)
        return all_chunks, all_metadata

    def process_tables_folder(self, folder: str):
        """Process all .csv files in a folder."""
        all_chunks, all_metadata = [], []
        for fname in os.listdir(folder):
            if fname.lower().endswith('.csv'):
                fpath = os.path.join(folder, fname)
                with open(fpath, newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row_idx, row in enumerate(reader):
                        as_text = " | ".join(f"{k}: {v}" for k, v in row.items())
                        all_chunks.append(as_text)
                        all_metadata.append({
                            "source": "table",
                            "chunk_id": len(all_chunks) - 1,
                            "table_csv": fname,
                            "row_idx": row_idx
                        })
        return all_chunks, all_metadata

    def process_faq_folder(self, folder: str):
        """Process all .json files as FAQ files in a folder."""
        all_chunks, all_metadata = [], []
        for fname in os.listdir(folder):
            if fname.lower().endswith('.json'):
                fpath = os.path.join(folder, fname)
                with open(fpath, 'r', encoding='utf-8') as f:
                    faqs = json.load(f)
                for i, item in enumerate(faqs):
                    chunk = f"Question: {item['question'].strip()}\nAnswer: {item['answer'].strip()}\nCategory: {item.get('category','').strip()}"
                    all_chunks.append(chunk)
                    all_metadata.append({"source": "faq", "chunk_id": len(all_chunks) - 1, "faq_file": fname})
        return all_chunks, all_metadata

    def get_openai_embeddings(self, texts: List[str]):
        """
        Call OpenAI embedding endpoint in batches. Returns list of list-of-floats.
        """
        embeddings = []
        batch_size = 100
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            response = self.client.embeddings.create(
                model=self.embed_model,
                input=batch
            )
            batch_embs = [item.embedding for item in response.data]
            embeddings.extend(batch_embs)
        return embeddings
    
    def embed_user_query(self, query_text):
        embedding = self.client.embeddings.create(
                model=self.embed_model,
                input=query_text
            )

        q_embedding = [item.embedding for item in embedding.data]
        return q_embedding


class DataIngestor:
    """
    Top-level class to orchestrate end-to-end processing and storage.
    """
    def __init__(
        self,
        pdf_dir: str,
        table_dir: str,
        docx_dir: str,
        faq_dir: str,
        chunk_size: int = None,
        chunk_overlap: int = None,
        embed_model: str = None,
        chroma_collection: str = None,
        chroma_path: str = "chroma"
    ):
        self.pdf_dir = pdf_dir
        self.table_dir = table_dir
        self.docx_dir = docx_dir
        self.faq_dir = faq_dir

        self.embedder = Embedder(chunk_size, chunk_overlap, embed_model)
        self.chroma_manager = ChromaManager(chroma_collection, chroma_path)

    def run(self):
        # 1. Process PDFs and Docx text
        pdf_chunks, pdf_metadata = self.embedder.process_text_folder(self.pdf_dir)
        docx_chunks, docx_metadata = self.embedder.process_text_folder(self.docx_dir)

        # 2. Process tables
        table_chunks, table_metadata = self.embedder.process_tables_folder(self.table_dir)

        # 3. Process FAQs
        faq_chunks, faq_metadata = self.embedder.process_faq_folder(self.faq_dir)

        # 4. Combine
        all_chunks = pdf_chunks + docx_chunks + table_chunks + faq_chunks
        all_metadata = pdf_metadata + docx_metadata + table_metadata + faq_metadata

        logging.info(f"Total chunks to embed: {len(all_chunks)}")

        embeddings = self.embedder.get_openai_embeddings(all_chunks)

        self.chroma_manager.ingest(all_chunks, all_metadata, embeddings)
        logging.info("Ingestion completed.")
