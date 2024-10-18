import re

def parse_output(ocr_text):
    parsed_data = {}

    # Example regex patterns for extracting data. You can modify these based on the structure of your OCR text.
    patterns = {
        'Name': r'(?i)(?:name|given name|full name):?\s*([a-zA-Z\s]+)',
        'Nationality': r'(?i)(?:nationality):?\s*([a-zA-Z\s]+)',
        'Place of Birth': r'(?i)(?:place of birth):?\s*([a-zA-Z\s,]+)',
        'Date of Birth': r'(?i)(?:date of birth|dob):?\s*(\d{2}/\d{2}/\d{4})',
        'Place of Issue': r'(?i)(?:place of issue):?\s*([a-zA-Z\s]+)',
        'Document Expiry': r'(?i)(?:expiry date):?\s*(\d{2}/\d{2}/\d{4})',
        'Additional Info': r'(?i)(?:additional info|remarks):?\s*(.*)',
        # Add more fields here as needed
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, ocr_text)
        if match:
            parsed_data[key] = match.group(1).strip()
        else:
            parsed_data[key] = 'Not found'

    return parsed_data
