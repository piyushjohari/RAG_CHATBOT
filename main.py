import os
import logging
import json
from datetime import datetime
from dotenv import load_dotenv

from src.parsers import Parsers
from src.crawlers import AngelOneFAQCrawler
from src.embeddings import DataIngestor
load_dotenv()

source_doc_dir = os.environ.get('SOURCE_DOCS_DIR')
pdf_text_dir = os.environ.get('OUTPUT_DIR_PDF_TEXT')
pdf_table_dir = os.environ.get('OUTPUT_DIR_PDF_TABLE')
docx_text_dir = os.environ.get('OUTPUT_DIR_DOCX_TEXT')
json_text_dir = os.environ.get('OUTPUT_DIR_SCRAPED_JSON')

def parse_source_docs(source_doc_folder):
    """
    This function parses the source docs(pdf, docx)
    and stores them in text and table(csv) format
    """
    parser = Parsers()
    for file_name in os.listdir(source_doc_folder):
        file_path = os.path.join(source_doc_folder, file_name)
        logging.info(f"Processing: {file_path}")
        if file_name.lower().endswith('.pdf'):
            prased_data = parser.parse(file_path=file_path, parser="pdfplumber")
        if file_name.lower().endswith('.docx'):
            prased_data = parser.parse(file_path=file_path, parser="docx")

def web_scrape_angelone_support():
    """
    This function crawl through the AngelOne support site
    to fetch all the FAQs available on the page and any of it's sub-page.
    """
    crawler = AngelOneFAQCrawler()
    data = crawler.crawl()
    dt = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    file_path = f"static/scraped_data/angelone_faqs_{dt}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    logging.info(f"Saved {len(data)} FAQ entries to {file_path}.")

if __name__ == "__main__":

    # Parse PDF and Docx
    parse_source_docs(source_doc_dir)

    # Scrape source URL
    web_scrape_angelone_support()

    # Chunking and Embedding
    ingestor = DataIngestor(
        pdf_dir=pdf_table_dir,
        table_dir=pdf_table_dir,
        docx_dir=docx_text_dir,
        faq_dir=json_text_dir
    )
    ingestor.run()

