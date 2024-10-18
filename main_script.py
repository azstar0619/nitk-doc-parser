from flask import Flask, request, jsonify, render_template
import os
from utils.extract_text_from_image import perform_ocr

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
    "mni": ["Manipuri", "mni"]
}

# Upload directory
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')  # This is where the upload form will be

# Route to upload and process image
@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    
    # Check if the user has uploaded a file
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    # Save the uploaded file in the uploads directory
    image_file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(image_file_path)
    
    # Perform OCR on the uploaded image
    source_language = 'eng'  # You can use your default or modify based on input
    extracted_text, _ = perform_ocr(image_file_path, source_language)
    
    # You can process the extracted text or return it directly
    return jsonify({"extracted_text": extracted_text})

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
