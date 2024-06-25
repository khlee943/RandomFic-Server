import pickle

import pandas as pd
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import re

from sklearn.decomposition import PCA
from unidecode import unidecode
from chat import preprocess_data, extract_features
import json

# Initialize VADER sentiment analyzer
sia = SentimentIntensityAnalyzer()

# Read in data
csv_file = '../all_fanfics.csv'
df = pd.read_csv(csv_file)
# Remove "Summary: " from the beginning of each row in the 'Text' column
df['Summary'] = df['Summary'].str.replace('Summary: ', '', regex=False)

# Print the first few rows to verify the changes
print(df.head())


def normalize_text(text):
    # Tokenize text
    tokens = nltk.word_tokenize(text)

    # Convert to lower case
    tokens = [token.lower() for token in tokens]

    # Remove punctuation and non-alphabetic words
    tokens = [token for token in tokens if token.isalpha()]

    # Join tokens back to string
    normalized_text = ' '.join(tokens)
    return normalized_text


df['normalized_summary'] = df['Summary'].apply(normalize_text)

# Function to perform sentiment analysis using VADER
def vader_sentiment(text):
    # Calculate sentiment score using VADER
    scores = sia.polarity_scores(text)
    sentiment_score = scores['compound']  # Use compound score as overall sentiment
    return sentiment_score

# Apply sentiment analysis functions to the 'Text' column
for index, row in df.iterrows():
    try:
        vader_score = vader_sentiment(row['normalized_summary'])
        df.loc[index, 'VADER_Sentiment'] = vader_score
        print(f"Row {index}: VADER Sentiment: {vader_score}")
    except Exception as e:
        print(f"Error processing row at index {index}: {e}")
        print(f"Row data: {row}")

# Function to remove non-BMP characters and convert to normal font
def remove_non_bmp_chars(text):
    # Convert to plain ASCII
    text = unidecode(text)
    # Remove any remaining non-BMP characters
    return re.sub(r'[^\x00-\xFFFF]', '', text)

# Apply the non-BMP character removal to 'Title' and 'Author' columns
df['Title'] = df['Title'].apply(remove_non_bmp_chars)
df['Author'] = df['Author'].apply(remove_non_bmp_chars)

# Processing for Recommendations
data = preprocess_data(csv_file)
tfidf_vectorizer, tfidf_matrix = extract_features(data)

# Do Principal Components Analysis to simplify the vectors by reducing number of dimensions/components
n_components = 100
pca = PCA(n_components=n_components)
tfidf_matrix_reduced = pca.fit_transform(tfidf_matrix)
print(tfidf_matrix_reduced.shape)

# Save PCA model if needed for later use
with open('../pca_model.pkl', 'wb') as f:
    pickle.dump(pca, f)
# Save tfidf_vectorizer if needed for later use
with open('../tfidf_vectorizer.pkl', 'wb') as f:
    pickle.dump(tfidf_vectorizer, f)

# Serialize vectors into JSON strings and add to df
df['Vector'] = [json.dumps(vector.tolist()) for vector in tfidf_matrix_reduced]

# Select relevant columns for the final dataframe
final_df = df[['Title', 'Author', 'Fandom', 'Url', 'Kudos', 'Summary', 'VADER_Sentiment', 'Content', 'Vector']]

# Rename the 'VADER_Sentiment' column to 'Average_Sentiment'
final_df.rename(columns={'VADER_Sentiment': 'Average_Sentiment'}, inplace=True)

# Save the final dataframe to a new CSV file
final_df.to_csv('fanfic_sentiment_analysis.csv', index=True, index_label='ID')