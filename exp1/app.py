from flask import Flask, request, render_template, send_file
import os
from utils import clean_tokens, extract_text_from_image, extract_text_from_pdf, fill_pdf_form, extract_data_with_ner, extract_data_with_regex

app = Flask(__name__)

# Upload folder setup
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        # Get the uploaded files
        file1 = request.files.get("file1")  # Template PDF
        file2 = request.files.get("file2")  # PDF/Image for text extraction

        # Save the uploaded files
        file1_path = os.path.join(UPLOAD_FOLDER, file1.filename)
        file2_path = os.path.join(UPLOAD_FOLDER, file2.filename)
        file1.save(file1_path)
        file2.save(file2_path)

        # Step 1: Extract text from the second file (PDF/Image)
        if file2.filename.lower().endswith('.pdf'):
            extracted_text = extract_text_from_pdf(file2_path)
        else:
            extracted_text = extract_text_from_image(file2_path)

        # Step 2: Clean and pre-process the text
        cleaned_tokens = clean_tokens(extracted_text.split())

        # Step 3: Extract useful information using NER and regex
        ner_data = extract_data_with_ner(extracted_text)
        regex_data = extract_data_with_regex(extracted_text)

        # Merge extracted data from NER and regex
        parsed_data = {**ner_data, **regex_data}

        # Step 4: Fill PDF form with extracted data
        filled_pdf_path = fill_pdf_form(file1_path, parsed_data)

        return render_template("upload.html",
                               original_file=file2.filename,
                               ocr_text=extracted_text,
                               parsed_data=parsed_data,
                               tokens=cleaned_tokens)  # Tokenized words

    return render_template("upload.html")


if __name__ == "__main__":
    app.run(debug=True)
