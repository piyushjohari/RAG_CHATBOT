import re
import pdfplumber

def clean_llm_csv(output_text) -> str:
    """
    Removes leading/trailing triple quotes, code blocks, or language tags (''' or ``` or ```csv) from LLM CSV output.
    Returns the raw CSV string.
    """
    # Remove leading/trailing whitespace and possible triple quotes at start
    text = output_text.strip()
    # Remove ''' or ``` or ```csv or ```CSV at start and end
    # Remove starting code block
    text = re.sub(r"^([`']{3,}(csv)?\s*)", "", text, flags=re.IGNORECASE)
    # Remove ending code block
    text = re.sub(r"([`']{3,})\s*$", "", text, flags=re.IGNORECASE)
    return text.strip()


# Unused Function
def extract_non_table_text(pdf_path) -> str:
    output = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_non_table_words = []
            # 1. Find all table cell bboxes
            try:
                tables = page.find_tables()
            except Exception as e:
                tables = []
            table_cells = []
            for table in tables:
                for row in table.cells:
                    for cell in row:
                        if cell is not None:
                            table_cells.append(cell)

            # 2. Get all words with coordinates on the page
            words = page.extract_words()
            for word in words:
                x0, y0, x1, y1 = word["x0"], word["top"], word["x1"], word["bottom"]
                # 3. Check if word bbox is outside all table cells
                in_table = False
                for cell in table_cells:
                    cx0, cy0, cx1, cy1 = cell.x0, cell.top, cell.x1, cell.bottom
                    # If word is fully inside any cell bbox
                    if x0 >= cx0 and x1 <= cx1 and y0 >= cy0 and y1 <= cy1:
                        in_table = True
                        break
                if not in_table:
                    page_non_table_words.append(word['text'])
            # Join the selected words in reading order
            output.append(" ".join(page_non_table_words))
    return "\n\n".join(output)
