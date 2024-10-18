import os
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import pytesseract
from PIL import Image
import fitz  # PyMuPDF
import io
from pdf2image import convert_from_path

app = Flask(__name__)

# Path configurations
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Make sure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Utility function to check if the file is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# OCR extraction from image
def extract_text_from_image(image_path):
    text = pytesseract.image_to_string(Image.open(image_path))
    return text

# OCR extraction from PDF using pdf2image
def extract_text_from_pdf_with_pdf2image(pdf_path):
    images = convert_from_path(pdf_path)
    text = ""
    for image in images:
        text += pytesseract.image_to_string(image)
    return text

# OCR extraction from PDF using PyMuPDF
def extract_text_from_pdf_with_pymupdf(pdf_path):
    pdf_document = fitz.open(pdf_path)
    recognized_text = ''
    
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)  # Load page
        pix = page.get_pixmap()  # Render page to an image
        img = Image.open(io.BytesIO(pix.tobytes()))  # Convert to PIL image
        text = pytesseract.image_to_string(img, lang='eng')  # OCR the image
        recognized_text += text + '\n'
    
    return recognized_text

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check if the post request has the files part
        if 'file1' not in request.files or 'file2' not in request.files:
            return redirect(request.url)
        
        file1 = request.files['file1']
        file2 = request.files['file2']
        
        if file1 and allowed_file(file1.filename) and file2 and allowed_file(file2.filename):
            filename1 = secure_filename(file1.filename)
            filename2 = secure_filename(file2.filename)
            
            file1_path = os.path.join(app.config['UPLOAD_FOLDER'], filename1)
            file2_path = os.path.join(app.config['UPLOAD_FOLDER'], filename2)
            
            file1.save(file1_path)
            file2.save(file2_path)
            
            # Perform OCR on the second file
            ocr_text = ""
            if filename2.rsplit('.', 1)[1].lower() in ['png', 'jpg', 'jpeg']:
                ocr_text = extract_text_from_image(file2_path)
            elif filename2.rsplit('.', 1)[1].lower() == 'pdf':
                # Here you can choose between PyMuPDF and pdf2image
                ocr_text = extract_text_from_pdf_with_pymupdf(file2_path)
                # or you could use extract_text_from_pdf_with_pdf2image(file2_path)
            else:
                ocr_text = "Unsupported file type"
            
            return render_template('upload.html', original_file=file2.filename, ocr_text=ocr_text)
    
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)
