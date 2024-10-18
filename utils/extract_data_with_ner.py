import spacy

nlp = spacy.load("en_core_web_sm")

def extract_data_with_ner(text):
    doc = nlp(text)
    extracted_data = {}
    
    for ent in doc.ents:
        if ent.label_ not in extracted_data:
            extracted_data[ent.label_] = [ent.text]
        else:
            extracted_data[ent.label_].append(ent.text)
    
    return extracted_data
