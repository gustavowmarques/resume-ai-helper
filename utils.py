
import os
import io
import re
from docx import Document
import PyPDF2

def extract_text_from_file(file_storage):
    filename = file_storage.filename.lower()
    if filename.endswith(".txt"):
        return file_storage.read().decode("utf-8")
    elif filename.endswith(".pdf"):
        reader = PyPDF2.PdfReader(file_storage)
        return "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
    elif filename.endswith(".docx"):
        doc = Document(file_storage.stream)
        return "\n".join(paragraph.text for paragraph in doc.paragraphs)
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
