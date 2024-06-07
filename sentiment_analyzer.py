import pandas as pd
import numpy as np
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import spacy
import re
from unidecode import unidecode

# Load the English language model in spaCy
nlp = spacy.load("en_core_web_lg")

# Initialize VADER sentiment analyzer
sia = SentimentIntensityAnalyzer()

# Read in data
df = pd.read_csv('all_fanfics.csv')
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

# # Function to perform sentiment analysis using spaCy
# def spacy_sentiment(text):
#     doc = nlp(text)
#     # Calculate sentiment score based on spaCy's built-in sentiment analysis
#     sentiment_score = doc._.sentiment.polarity
#     return sentiment_score

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

# Select relevant columns for the final dataframe
final_df = df[['Title', 'Author', 'Fandom', 'Url', 'Kudos', 'VADER_Sentiment']]

# Rename the 'VADER_Sentiment' column to 'Average_Sentiment'
final_df.rename(columns={'VADER_Sentiment': 'Average_Sentiment'}, inplace=True)

# Save the final dataframe to a new CSV file
final_df.to_csv('fanfic_sentiment_analysis.csv', index=True)