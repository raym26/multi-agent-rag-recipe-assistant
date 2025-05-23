import os
import fitz  # PyMuPDF
import re

from dotenv import load_dotenv

os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

def load_environment():
    """Load environment variables from .env file."""
    load_dotenv()
    # Ensure API keys are set
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable not set")
    os.environ["GROQ_API_KEY"] = api_key

    # Database URL
    db_url = os.getenv("DB_URL", "postgresql+psycopg://ai:ai@localhost:5532/ai")
    return db_url


def get_example_queries():
    """Return a list of example queries for the PDF assistant."""
    return [
        "What kinds of recipes are in the cookbook?",
        "Please list all the recipes in the cookbook.",
        "Please show me the the total cooking time.",

    ]


def get_filename_from_url(url):
    """Extract the filename from a URL."""
    return url.split('/')[-1]



def extract_recipe_titles_from_pdf(pdf_path):
    """
    Extract potential recipe titles from a PDF by scanning for bold headers or patterns.
    Returns a list of unique recipe titles.
    """
    doc = fitz.open(pdf_path)
    titles = set()

    # Define a regex pattern for typical recipe titles (can be adjusted)
    title_pattern = re.compile(r'^[A-Z][A-Za-z\s,-]{3,}$')

    for page in doc:
        blocks = page.get_text("dict")['blocks']
        for block in blocks:
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = span["text"].strip()
                    if span.get("font", "").lower().startswith("bold") or span.get("flags", 0) & 2:
                        if title_pattern.match(text):
                            titles.add(text)

    return sorted(titles)