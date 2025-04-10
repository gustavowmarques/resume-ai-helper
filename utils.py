
import os
import io
import re
from docx import Document
import PyPDF2
import pdfplumber
from werkzeug.utils import secure_filename

def extract_text_from_file(file):
    filename = secure_filename(file.filename)
    ext = os.path.splitext(filename)[1].lower()

    if ext == ".txt":
        return file.read().decode("utf-8")
    elif ext == ".pdf":
        with pdfplumber.open(file) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    elif ext == ".docx":
        doc = Document(file)
        return "\n".join(p.text for p in doc.paragraphs)
    else:
        raise ValueError("Unsupported file type")
    
def extract_contact_info(job_description):
    email_match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", job_description)
    phone_match = re.search(r"\+?\d[\d\s\-()]{7,}\d", job_description)

    contact = []
    if email_match:
        contact.append(f"Email: {email_match.group()}")
    if phone_match:
        contact.append(f"Phone: {phone_match.group()}")

    return " | ".join(contact) if contact else "Not provided"

def generate_docx_file(text):
    doc = Document()
    for line in text.split("\n"):
        doc.add_paragraph(line)
    file_stream = io.BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    return file_stream

def create_zip(files: dict, zip_name="output.zip"):
    import zipfile
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for filename, content in files.items():
            zip_file.writestr(filename, content.getvalue())
    zip_buffer.seek(0)
    return zip_buffer

def extract_job_description_from_url(job_url):
    import requests
    from bs4 import BeautifulSoup

    try:
        response = requests.get(job_url, timeout=5)
        response.raise_for_status()  # Raises HTTPError for bad responses
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract both paragraphs and list items
        paragraphs = soup.find_all(["p", "li"])
        job_description = "\n".join(p.get_text() for p in paragraphs).strip()

        return job_description or None
    except Exception as e:
        return f"Error: {str(e)}"