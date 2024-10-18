import re
from pdfrw import PdfReader, PdfWriter, PdfName, PdfString

def clean_text(text):
    """
    Cleans the OCR text by removing special characters and digits,
    leaving only lowercase alphabetic characters and spaces.
    """
    # Remove special characters and digits
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    text = re.sub(r'\s+', ' ', text)  # Remove extra spaces
    return text.lower().strip()

def parse_output(text, nlp):
    """
    Extracts entities from the OCR text using Named Entity Recognition (NER) and/or regex.

    Args:
    - text: Cleaned OCR text.
    - nlp: The loaded spaCy model for NER.

    Returns:
    - A dictionary of parsed data (entities like names, dates, and other fields).
    """
    doc = nlp(text)
    parsed_data = {}

    # Extract entities using NER
    for ent in doc.ents:
        if ent.label_ in ['PERSON', 'ORG', 'DATE', 'GPE', 'MONEY']:  # Adjust these as needed
            parsed_data[ent.label_] = ent.text

    return parsed_data

def fill_pdf_form(template_path, data):
    """
    Fills a PDF form with the parsed data.
    
    Args:
    - template_path: The path to the PDF template.
    - data: The parsed data to fill in the PDF form.

    Returns:
    - The path to the filled PDF.
    """
    reader = PdfReader(template_path)
    for page in reader.pages:
        annotations = page.get('/Annots')
        if annotations:
            for annotation in annotations:
                field_name = annotation.get('/T')
                if field_name:
                    field_name = field_name[1:-1]  # Get the field name without parentheses
                    if field_name in data:
                        annotation.update({
                            PdfName("/V"): PdfString(data[field_name])  # Fill with parsed data
                        })
    filled_path = template_path.replace(".pdf", "_filled.pdf")
    PdfWriter(filled_path, trailer=reader).write()
    return filled_path
