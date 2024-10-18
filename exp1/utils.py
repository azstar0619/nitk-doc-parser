import re

def parse_output(ocr_text):
    # Initialize an empty dictionary to hold the key-value pairs
    parsed_data = {}

    # Example regex patterns for extracting data. You can modify these based on the structure of your OCR text.
    patterns = {
        'Name': r'(?i)(?:name|given name|full name):?\s*([a-zA-Z\s]+)',
        'Surname': r'(?i)(?:surname|family name):?\s*([\w\s]+)',
        'Nationality': r'(?i)(?:nationality|citizenship):?\s*([a-zA-Z\s]+)',
        'Place of Birth': r'(?i)(?:place of birth):?\s*([a-zA-Z\s,]+)',
        'Date of Birth': r'(?i)(?:date of birth|dob):?\s*(\d{2}/\d{2}/\d{4})',
        'Place of Issue': r'(?i)(?:place of issue):?\s*([a-zA-Z\s]+)',
        'Document Expiry': r'(?i)(?:expiry date):?\s*(\d{2}/\d{2}/\d{4})',
        'Additional Info': r'(?i)(?:additional info|remarks):?\s*(.*)',
        'Address': r'(?i)(?:address|residential address):?\s*([\w\s,]+)',
        'Contact Number': r'(?i)(?:contact number|phone number):?\s*([\d\s-]+)',
        'Email': r'(?i)(?:email|e-mail):?\s*([\w\.-]+@[\w\.-]+)',
        'Gender': r'(?i)(?:gender):?\s*(male|female|other)',
        'Marital Status': r'(?i)(?:marital status):?\s*([\w\s]+)',
        'Occupation': r'(?i)(?:occupation|profession):?\s*([\w\s]+)',
        'Emergency Contact': r'(?i)(?:emergency contact):?\s*([\w\s,]+)',
    }

    # Loop through each pattern and try to find matches in the output
    for key, pattern in patterns.items():
        match = re.search(pattern, ocr_text)
        if match:
            parsed_data[key] = match.group(1).strip()  # Capture and clean the value
        else:
            parsed_data[key] = 'Not found'

    return parsed_data
