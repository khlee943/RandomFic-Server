import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer

def preprocess_data(file_path):
    data = pd.read_csv(file_path)
    return data

def extract_features(data):
    # Concatenate Fandom, Content, and Summary into a single string
    combined_text = data['Fandom'] + ' ' + data['Content'] + ' ' + data['Summary']
    # Convert text data to TF-IDF vectors
    tfidf_vectorizer = TfidfVectorizer(stop_words='english')
    tfdif_fanfic_content = tfidf_vectorizer.fit_transform(combined_text)
    return tfidf_vectorizer, tfdif_fanfic_content