import os
import pytesseract
import spacy
from flask import Flask, render_template, request, url_for
from werkzeug.utils import secure_filename
from pdf2image import convert_from_path
from PyPDF2 import PdfReader
from utils import parse_output, clean_text, fill_pdf_form
import logging

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads/'
PROCESSED_IMAGES_FOLDER = 'static/processed_images/'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'bmp'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_IMAGES_FOLDER'] = PROCESSED_IMAGES_FOLDER

logging.basicConfig(level=logging.DEBUG)

# Load spaCy model for NER and Tokenization
nlp = spacy.load("en_core_web_sm")

# Function to check if the uploaded file is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to perform OCR on PDF by converting it to images first
def ocr_from_pdf(pdf_path):
    """
    Converts PDF to images and performs OCR on all pages.
    """
    images = convert_from_path(pdf_path)
    ocr_text = ''
    for page_num, image in enumerate(images):
        # Use pytesseract to extract text from each image (page)
        ocr_text += pytesseract.image_to_string(image)
    return ocr_text

# Function to extract text from plain PDF using PyPDF2
def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ''
    for page in reader.pages:
        text += page.extract_text()
    return text

# Tokenize the text using spaCy
def tokenize_text(text):
    """
    Tokenizes the text using spaCy.
    Returns a list of tokens.
    """
    doc = nlp(text)
    tokens = [token.text for token in doc]  # Tokenize and extract words
    return tokens

# Home route
@app.route('/', methods=['GET', 'POST'])
def home():
    ocr_text = None
    original_file = None
    parsed_data = None
    tokens = None

    if request.method == 'POST':
        # Handle first file (template) and second file (source for OCR)
        if 'file2' not in request.files:
            return "No file part"
        
        file1 = request.files['file1']  # Template file for form filling
        file2 = request.files['file2']  # Source file for OCR

        if file2 and allowed_file(file2.filename):
            original_file = secure_filename(file2.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], original_file)
            file2.save(file_path)

            # Check if the file is a PDF or an image
            if file2.filename.rsplit('.', 1)[1].lower() == 'pdf':
                # Try to extract text from PDF using PyPDF2, if not images
                try:
                    ocr_text = extract_text_from_pdf(file_path)
                except:
                    # If PyPDF2 fails, fallback to OCR
                    ocr_text = ocr_from_pdf(file_path)
            else:
                # Perform OCR on the image (file)
                ocr_text = pytesseract.image_to_string(file_path)

            logging.debug(f"OCR Text: {ocr_text}")

            # Clean and preprocess the extracted text
            clean_text_data = clean_text(ocr_text)
            logging.debug(f"Cleaned Text: {clean_text_data}")

            # Tokenize the cleaned text
            tokens = tokenize_text(clean_text_data)
            logging.debug(f"Tokens: {tokens}")

            # Parse the OCR text using regex and NER
            parsed_data = parse_output(clean_text_data, nlp)
            logging.debug(f"Parsed Data: {parsed_data}")

            # Fill the PDF form using the parsed data
            if file1 and allowed_file(file1.filename):
                template_file = secure_filename(file1.filename)
                template_path = os.path.join(app.config['UPLOAD_FOLDER'], template_file)
                file1.save(template_path)

                # Fill the PDF form with parsed data
                filled_pdf_path = fill_pdf_form(template_path, parsed_data)
                logging.debug(f"Filled PDF Path: {filled_pdf_path}")
            else:
                filled_pdf_path = None

            # Save the processed image (just save the original file for now)
            processed_image_path = os.path.join(PROCESSED_IMAGES_FOLDER, 'processed_image.png')
            file2.save(processed_image_path)  # Save the original image as a placeholder for the processed image
            
            # Return the result to the template
            return render_template('upload.html', 
                                   ocr_text=ocr_text, 
                                   original_file=original_file,
                                   parsed_data=parsed_data,
                                   filled_pdf_path=filled_pdf_path,
                                   tokens=tokens,
                                   processed_image_url=url_for('static', filename='processed_images/processed_image.png'))
    
    return render_template('upload.html')

# Main application entry point
if __name__ == '__main__':
    app.run(debug=True)
