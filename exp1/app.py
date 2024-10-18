import os
import pytesseract
from flask import Flask, render_template, request, url_for
from werkzeug.utils import secure_filename
from pdf2image import convert_from_path
from utils import parse_output  # Assuming parse_output is implemented in utils.py
import logging

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads/'
PROCESSED_IMAGES_FOLDER = 'static/processed_images/'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'bmp'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_IMAGES_FOLDER'] = PROCESSED_IMAGES_FOLDER

logging.basicConfig(level=logging.DEBUG)

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

# Home route
@app.route('/', methods=['GET', 'POST'])
def home():
    ocr_text = None
    original_file = None
    parsed_data = None

    if request.method == 'POST':
        # Handle first file (template) and second file (source for OCR)
        if 'file2' not in request.files:
            return "No file part"
        
        file1 = request.files['file1']
        file2 = request.files['file2']

        if file2 and allowed_file(file2.filename):
            original_file = secure_filename(file2.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], original_file)
            file2.save(file_path)

            # Check if the file is a PDF
            if file2.filename.rsplit('.', 1)[1].lower() == 'pdf':
                # Perform OCR on the PDF (convert to image first)
                ocr_text = ocr_from_pdf(file_path)
            else:
                # Perform OCR on the image (file)
                ocr_text = pytesseract.image_to_string(file_path)

            logging.debug(f"OCR Text: {ocr_text}")
            
            # Parse the OCR text
            parsed_data = parse_output(ocr_text)
            logging.debug(f"Parsed Data: {parsed_data}")

            # Save the processed image (just save the original file for now)
            processed_image_path = os.path.join(PROCESSED_IMAGES_FOLDER, 'processed_image.png')
            file2.save(processed_image_path)  # Save the original image as a placeholder for the processed image
            
            # Return the result to the template
            return render_template('upload.html', 
                                   ocr_text=ocr_text, 
                                   original_file=original_file,
                                   parsed_data=parsed_data,
                                   processed_image_url=url_for('static', filename='processed_images/processed_image.png'))
    
    return render_template('upload.html')

# Main application entry point
if __name__ == '__main__':
    app.run(debug=True)
