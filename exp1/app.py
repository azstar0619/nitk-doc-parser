import os
from flask import Flask, render_template, request, redirect, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract

app = Flask(__name__)

# Path configurations
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'static/processed_images'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

# Make sure the folders exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(PROCESSED_FOLDER):
    os.makedirs(PROCESSED_FOLDER)

# Utility function to check if the file is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Preprocess image: sharpen, increase contrast, and reduce noise
def preprocess_image(image_path):
    img = Image.open(image_path)
    
    # Enhance sharpness
    sharpness_enhancer = ImageEnhance.Sharpness(img)
    img = sharpness_enhancer.enhance(2)  # Increase the sharpness by factor of 2
    
    # Increase the contrast
    contrast_enhancer = ImageEnhance.Contrast(img)
    img = contrast_enhancer.enhance(1.5)  # Increase contrast by factor of 1.5
    
    # Apply a slight blur to reduce noise
    img = img.filter(ImageFilter.MedianFilter())
    
    # Save the processed image for preview
    processed_image_path = os.path.join(app.config['PROCESSED_FOLDER'], 'processed_image.png')
    img.save(processed_image_path)
    
    print(f"Processed image saved at: {processed_image_path}")  # Debugging output to check if the file is saved
    return img

# OCR extraction function
def extract_text_from_image(image_path):
    img = preprocess_image(image_path)
    text = pytesseract.image_to_string(img)
    return text

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
            ocr_text = extract_text_from_image(file2_path)
            
            return render_template('upload.html', original_file=file2.filename, ocr_text=ocr_text)
    
    return render_template('upload.html')

@app.route('/static/processed_images/<filename>')
def send_processed_file(filename):
    return send_from_directory(app.config['PROCESSED_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
