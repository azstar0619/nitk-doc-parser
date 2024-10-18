from flask import Flask, request, jsonify, render_template, send_file
import os
from utils.extract_text_from_image import perform_ocr
from utils.fill_pdf_form import fill_pdf_form  # Assuming this function exists
from utils.tokenizer_utils import tokenize_text  # Import tokenizer function
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Language mappings
language_mappings = {
    "hi": ["Hindi", "hin"],
    "ur": ["Urdu", "urd"],
    "pa": ["Punjabi", "pan"],
    "gu": ["Gujarati", "guj"],
    "mr": ["Marathi", "mar"],
    "te": ["Telugu", "tel"],
    "kn": ["Kannada", "kan"],
    "ml": ["Malayalam", "mal"],
    "ta": ["Tamil", "tam"],
    "or": ["Odia", "ori"],
    "bn": ["Bengali", "ben"],
    "as": ["Assamese", "asm"],
    "mni": ["Manipuri", "mni"],
    "eng": ["English", "eng"]  # Added English mapping
}

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

# Upload directory
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Helper function to check if file type is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload-image', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type. Only PNG, JPG, JPEG are allowed."}), 400
    
    # Save the uploaded file in the uploads directory
    image_file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
    file.save(image_file_path)
    
    # Perform OCR on the uploaded image
    source_language = request.form.get('language', 'eng')  # Set to 'eng' by default
    if source_language not in language_mappings:
        return jsonify({"error": f"Unsupported language: {source_language}"}), 400
    
    extracted_text, _ = perform_ocr(image_file_path, source_language)
    
    # Tokenize the extracted text
    tokens = tokenize_text(extracted_text)
    
    # Return the extracted text and its tokens
    return jsonify({"extracted_text": extracted_text, "tokens": tokens})

@app.route('/upload-pdf', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type. Only PNG, JPG, JPEG, PDF are allowed."}), 400
    
    # Save the uploaded file in the uploads directory
    pdf_file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
    file.save(pdf_file_path)
    
    # Assuming parsed_data comes from another part of the application
    parsed_data = {"Field1": "Data1", "Field2": "Data2"}  # Replace with actual parsed data
    
    # Fill the PDF form
    filled_pdf_path = fill_pdf_form(pdf_file_path, parsed_data)
    
    return jsonify({"filled_pdf_path": filled_pdf_path})

@app.route('/download/<filename>')
def download_file(filename):
    # Correct path to file using the UPLOAD_FOLDER only once
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    # Check if the file exists
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404
    
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
