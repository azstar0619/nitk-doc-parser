import re

def extract_data_with_regex(text):
    phone_numbers = re.findall(r'\b\d{10}\b', text)
    dates = re.findall(r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b', text)
    
    extracted_data = {
        'phone_numbers': phone_numbers,
        'dates': dates
    }
    
    return extracted_data
