import pytesseract
from PIL import Image

def perform_ocr(image_file_path: str, language: str = "eng") -> tuple:
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    
    with Image.open(image_file_path) as source_image:
        image_text = pytesseract.image_to_string(source_image, lang=language)

    return (image_text, image_file_path)
