import fitz  # PyMuPDF
import re
from typing import List
from urllib.request import urlopen
from tempfile import NamedTemporaryFile

def extract_recipe_titles(pdf_url: str) -> List[str]:
    """
    Extract recipe titles from the PDF using simple heuristics:
    - Detect lines in bold or large font
    - Use regex to find lines that look like recipe names
    """
    titles = set()
    try:
        # Download the PDF temporarily
        with urlopen(pdf_url) as response, NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(response.read())
            tmp_path = tmp_file.name

        doc = fitz.open(tmp_path)

        for page in doc:
            blocks = page.get_text("dict")['blocks']
            for block in blocks:
                if 'lines' not in block:
                    continue
                for line in block['lines']:
                    for span in line['spans']:
                        text = span['text'].strip()
                        if not text or len(text.split()) > 12:
                            continue
                        if span['size'] >= 11 and re.match(r"^[A-Z][A-Za-z\s,'()&-]+$", text):
                            titles.add(text)

        return list(titles)

    except Exception as e:
        print(f"Error extracting recipe titles: {e}")
        return []
