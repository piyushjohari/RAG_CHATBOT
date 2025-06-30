# RAG Chatbot - Insurance Document Assistant

## How to Use

1. Duplicate the `.env.example` file and rename it to `.env`.
2. Add your OpenAI API key as `OPENAI_API_KEY` in the `.env` file.
3. Update the `MODEL` and `EMBED_MODEL` variables if needed; defaults are `gpt-4o` and `text-embedding-3-small` respectively.
4. Update the path for source files by setting `SOURCE_DOCS_DIR`; otherwise, source files will be stored at `static/insurance_data` by default.
5. Create a virtual environment:
    - Using [virtualenv](https://virtualenv.pypa.io/en/stable/):  
      ```bash
      virtualenv venv
      ```
      or use any other tool of choice.
6. Activate the virtual environment:  
    - **Windows:**  
      ```bash
      .\venv\Scripts\activate
      ```
    - **Linux/Mac:**  
      ```bash
      source venv/bin/activate
      ```
7. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
8. Run the `main.py` file. This may take some time, as it parses, webscrapes, chunks, and embeds the data.
    ```bash
    python main.py
    ```
9. Launch the chatbot Streamlit app:
    ```bash
    streamlit run rag_chatbot_app.py
    ```

---

## Sample Queries

1. How to get dividend information?
2. Why did my orders get cancelled?
3. If you visit a health care provider’s office or clinic, special visit what are the charges for bronze plan?
4. Do you need a referral to see a specialist?
5. What is the out-of-pocket limit for the bronze plan?
6. For getting an X-Ray in the copper plan, how much will I be charged?
7. I am pregnant, how much will I be charged?
8. What are the limitations and exceptions for outpatient surgery facility fees for the 2500 gold plan?
9. I have type 1 diabetes, am I eligible for 7350 copper plan?

---

## Assumptions

1. Only PDF and DOCX documents are processed.
2. Web scraping is limited to the AngelOne support page, which is a static page with minimal AJAX.
3. While conversation history is visible on the Streamlit app, context history is not currently utilized for LLM response generation.
4. Only open-source libraries were used for PDF parsing. Given the complexity of tables in PDFs, more specialized tools may further enhance table extraction accuracy.

---

## Notes

1. While it was technically feasible to embed and store data during in-memory processing, data processing and visualization have been kept separate to enhance transparency and clarity.
2. Although Camelot consistently extracted a single table per page, it resulted in significant data loss. As such, `pdfplumber` was chosen to ensure more comprehensive data capture.

---

## Areas for Improvement

1. **Filter Irrelevant Tables:** Implement mechanisms to filter out superfluous tables lacking relevant information to reduce unnecessary LLM calls and processing time.
2. **Parallel Processing:** Introduce parallelization at various workflow stages to greatly improve efficiency and throughput.
3. **Dependency Cleanup:** The current `requirements.txt` includes some unutilized libraries; a thorough review and cleanup is recommended.
4. **Pipeline Design:** Parsing and embedding processes can be encapsulated into a robust pipeline, enabling automated execution whenever new or modified source documents are uploaded. This ensures only novel or updated documents are processed, optimizing resource usage.
5. **API Deployment:** The conversational interface can be exposed as an API, enabling seamless integration with web-based chatbot UIs for enhanced user experience.
6. **Additional Validation:** More checks and validations could be incorporated for greater robustness, though this has been deprioritized for the current version.

---

**Feel free to raise issues or suggestions for further improvements!**