import io
import json
import logging
import pandas as pd
from docx import Document
from PyPDF2 import PdfReader
from llm_integration import generate_ad_copy

def extract_text_from_excel(file_stream):
    try:
        df = pd.read_excel(file_stream)
        # Convert dataframe to CSV text for easier analysis.
        return df.to_csv(index=False)
    except Exception as e:
        logging.error(f"Error reading Excel file: {e}")
        return ""

def extract_text_from_docx(file_stream):
    try:
        document = Document(file_stream)
        full_text = [para.text for para in document.paragraphs]
        return "\n".join(full_text)
    except Exception as e:
        logging.error(f"Error reading DOCX file: {e}")
        return ""

def extract_text_from_pdf(file_stream):
    try:
        reader = PdfReader(file_stream)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    except Exception as e:
        logging.error(f"Error reading PDF file: {e}")
        return ""

def extract_text_from_plain(file_stream):
    try:
        return file_stream.read().decode('utf-8')
    except Exception as e:
        logging.error(f"Error reading plain text file: {e}")
        return ""

def extract_schedule_from_text(text):
    """
    Use LLM to extract schedule items from text.
    The prompt instructs the model to output a JSON list with keys:
    'name', 'start_date', and 'end_date' (dates in YYYY-MM-DD format).
    """
    prompt = (
        "Extract all ad campaign schedule items from the following document in JSON format. "
        "Each item should be an object with keys 'name', 'start_date', and 'end_date', where the dates are in YYYY-MM-DD format. "
        "Return only valid JSON.\n\n"
        f"{text}"
    )
    # Use default model "llama3.2" for extraction.
    result = generate_ad_copy(prompt, "llama3.2")
    try:
        data = json.loads(result)
        return data
    except Exception as e:
        logging.error(f"Error parsing JSON from LLM output: {e}")
        return []

def process_schedule_document(file):
    filename = file.filename
    file_ext = filename.split('.')[-1].lower()
    text = ""
    if file_ext in ["xls", "xlsx"]:
        text = extract_text_from_excel(file)
    elif file_ext == "pdf":
        text = extract_text_from_pdf(file)
    elif file_ext == "docx":
        text = extract_text_from_docx(file)
    else:
        text = extract_text_from_plain(file)
    campaigns = extract_schedule_from_text(text)
    return campaigns
