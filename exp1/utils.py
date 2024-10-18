import spacy
import re
from PyPDF2 import PdfReader
from pdfrw import PdfWriter, PdfReader as PdfFormReader, PdfDict, PdfName, PdfString
import pytesseract
from PIL import Image

# Load spaCy model for Named Entity Recognition (NER)
nlp = spacy.load("en_core_web_sm")

# Function to extract text from a PDF using PyPDF2
def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# Function to extract text from an image using OCR
def extract_text_from_image(image_file):
    image = Image.open(image_file)
    text = pytesseract.image_to_string(image)
    return text

# Tokenization, cleaning, and preserving key short tokens like "M", "F"
def clean_tokens(tokens):
    """
    Clean tokens by removing irrelevant characters but keep meaningful short tokens like 'M', 'F', etc.
    """
    # List of short tokens to preserve (e.g., gender markers, country codes, initials)
    preserve_short_tokens = ['M', 'F', 'X', 'Y', 'Z']  # Add more relevant short tokens as needed
    
    cleaned_tokens = []
    for token in tokens:
        # Preserve meaningful short tokens (e.g., 'M' or 'F') and alphanumeric strings
        if token.isalnum() and (len(token) > 2 or token.upper() in preserve_short_tokens):
            cleaned_tokens.append(token)
    
    return cleaned_tokens

# Function to extract data using spaCy's NER
def extract_data_with_ner(text):
    doc = nlp(text)
    extracted_data = {}
    
    for ent in doc.ents:
        if ent.label_ not in extracted_data:
            extracted_data[ent.label_] = [ent.text]  # Create a list for multiple entities
        else:
            extracted_data[ent.label_].append(ent.text)  # Append multiple entities
    
    return extracted_data

# Function to extract data using regular expressions (regex)
def extract_data_with_regex(text):
    # Example regex for extracting phone numbers and dates
    phone_numbers = re.findall(r'\b\d{10}\b', text)  # Matches 10-digit phone numbers
    dates = re.findall(r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b', text)  # Matches common date formats
    
    extracted_data = {
        'phone_numbers': phone_numbers,
        'dates': dates
    }
    
    return extracted_data

# Function to fill PDF form using pdfrw
def fill_pdf_form(template_path, parsed_data):
    reader = PdfFormReader(template_path)
    writer = PdfWriter()

    for page in reader.pages:
        annotations = page['/Annots']
        if annotations:
            for annotation in annotations:
                # Check if annotation has a field name ('/T')
                if '/T' in annotation:
                    field_name = annotation.get('/T')[1:-1]  # Extract field name, strip the surrounding quotes
                    if field_name in parsed_data:
                        annotation.update({
                            PdfName('/V'): PdfString(parsed_data[field_name])  # Set the value in the field
                        })
        writer.addpage(page)
    
    output_path = template_path.replace('.pdf', '_filled.pdf')
    writer.write(output_path)
    return output_path

