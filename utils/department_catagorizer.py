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
    raw_text = "".join([char.lower() for char in raw_text if char not in string.punctuation])
    tokenized_text = " ".join([lemmatizer.lemmatize(word) for word in re.split(r'\W+', raw_text) if word not in common_words])
    return tokenized_text

dataframe["cleaned_text"] = dataframe["text"].apply(preprocess_text)
vectorizer.fit_transform(dataframe["cleaned_text"])
