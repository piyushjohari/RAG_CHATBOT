TABLE_DATA_PARSING_PROMPT = """
You are an expert in interpreting and cleaning tabular data extracted from PDFs.

**Task Goal:**  
The following table, as parsed from a PDF using pdfplumber, has all its data captured but the content may be disoriented:
- Some values that belong to a single row in the original PDF may be split across multiple rows or columns here.
- Table cells may be misaligned or wrapped across multiple lines/rows.
- Values from merged cells in the original PDF may appear fragmented here.
- There may be extra blank rows, duplicated headers, or columns with misplaced values.

**Your Tasks:**
1. **Carefully analyze the provided parsed table.**
2. **Mentally reconstruct how the actual table looked in the PDF.**  
    - Group or merge values that belong to the same cell, row, or column.
    - Fix rows whose data is spread across multiple rows in the extracted content.
    - Align values into the correct columns, recreating the original logical structure.
3. **Remove artifact rows** (e.g., duplicated headers, empty/non-informative rows).
4. **Recreate and present the cleaned table in proper markdown table format.**
5. **If something cannot be reliably reconstructed, use your best judgment and document your assumptions.**

**Input 
1. Parsed Table: the parsed table from a pdf.
2. filename: file name from where this table data was extracted.
**


**Output:**
- The cleaned and best-guess accurate data.
- add the filename in each row of the csv
- Please provide only the cleaned table as raw CSV text, using commas as delimiter, with one header row and no extra text.  

**DO NOT include the raw input table in your output. Only the cleaned table without any extra comments added**
**ONLY return the table data in csv format without any extra character like '''**


"""

TABLE_DATA_TUNING_PROMPT = """
You are an expert in interpreting and cleaning tabular data extracted from PDFs.

**Task Goal:**  
The following table, as parsed from a PDF using pdfplumber, has all its data captured but the content may be disoriented:
- Some values that belong to a single row in the original PDF may be split across multiple rows or columns here.
- Table cells may be misaligned or wrapped across multiple lines/rows.
- Values from merged cells in the original PDF may appear fragmented here.
- There may be extra blank rows, duplicated headers, or columns with misplaced values.

**Your Tasks:**
1. **Carefully analyze the provided parsed table.**
2. **Carefully analyze the provided line by line text data.**
2. **Mentally reconstruct how the actual table looked in the PDF.**  
    - Group or merge values that belong to the same cell, row, or column.
    - Fix rows whose data is spread across multiple rows in the extracted content.
    - Align values into the correct columns, recreating the original logical structure.
3. **Remove artifact rows** (e.g., duplicated headers, empty/non-informative rows).
4. **Recreate and present the cleaned table in proper markdown table format.**
5. **If something cannot be reliably reconstructed, use your best judgment and document your assumptions.**

**Input 
1. Parsed Text: This will be a line by line text, which will contain both normal text as well table text.
2. Parsed Table: This is the parsed table data as markdown
**

**Output:**
- The cleaned and best-guess accurate data.
- Please provide only the cleaned table as raw CSV text, using commas as delimiter, with one header row and no extra text.  

**DO NOT include the raw input table in your output. Only the cleaned table without any extra comments added**
**ONLY return the table data in csv format without any extra character like '''**
"""
