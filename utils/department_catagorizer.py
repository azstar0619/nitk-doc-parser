import string
import re
import nltk
import pandas as pd
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib

# Load model and vectorizer
trained_model = joblib.load(r'department_model\SupportVectorMachine.pkl')
vectorizer = TfidfVectorizer()
dataframe = pd.read_csv(r'Backend\Models\data-1.csv', usecols=["department", "text"])

common_words = set(stopwords.words("english"))
lemmatizer = nltk.WordNetLemmatizer()

def categorize_department(text: str) -> str:
    cleaned_text = preprocess_text(text)
    processed_text = vectorizer.transform([cleaned_text])
    predicted_department = trained_model.predict(processed_text)[0]
    return predicted_department

def preprocess_text(raw_text: str) -> str:
    print(f"Original Text: {raw_text}")  # Print original text
    raw_text = "".join([char.lower() for char in raw_text if char not in string.punctuation])
    print(f"Cleaned Text: {raw_text}")  # Print cleaned text (no punctuation, lowercased)
    
    # Tokenize and remove non-alphabetic tokens
    tokenized_text = " ".join([lemmatizer.lemmatize(word) for word in re.split(r'\W+', raw_text) if word not in common_words and word.isalpha()])
    print(f"Tokenized and Lemmatized Text: {tokenized_text}")  # Print tokenized and lemmatized text
    return tokenized_text

# Apply preprocessing and print cleaned and tokenized text for each row
dataframe["cleaned_text"] = dataframe["text"].apply(preprocess_text)

# Fit the vectorizer on the cleaned text
vectorizer.fit_transform(dataframe["cleaned_text"])
