import pdfplumber
from docx import Document
import os

def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
    return text

def extract_text_from_docx(docx_path):
    doc = Document(docx_path)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_text_from_txt(txt_path):
    with open(txt_path, "r", encoding="utf-8") as file:
        return file.read()

def process_documents(folder_path):
    """Extract text from all documents in a folder."""
    documents = {}
    
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if filename.endswith(".pdf"):
            documents[filename] = extract_text_from_pdf(file_path)
        elif filename.endswith(".docx"):
            documents[filename] = extract_text_from_docx(file_path)
        elif filename.endswith(".txt"):
            documents[filename] = extract_text_from_txt(file_path)

    return documents
