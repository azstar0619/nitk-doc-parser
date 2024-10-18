import nltk
nltk.download('punkt')  # Download the punkt tokenizer models

def tokenize_text(text):
    # Tokenize text into words
    tokens = nltk.word_tokenize(text)
    return tokens
