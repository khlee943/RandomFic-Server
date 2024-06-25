import gc
import pickle
import random

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def preprocess_data(file_path):
    data = pd.read_csv(file_path)
    return data

def extract_features(data):
    # Concatenate Title, Author, Fandom, Summary, and Content into a single string
    combined_text = data['Title'] + ' ' + data['Author'] + ' ' + data['Fandom'] + ' ' + data['Summary'] + ' ' + data[
        'Content']
    # Convert text data to TF-IDF vectors
    tfidf_vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf_vectorizer.fit_transform(combined_text)
    return tfidf_vectorizer, tfidf_matrix

# def recommend_fanfic(user_input, tfidf_vectorizer, fanfics):
#     try:
#         # Randomly select a fanfic from the list
#         recommended_fanfic = random.choice(fanfics)
#
#         response_text = f"User: {user_input}\nAI: Based on your interest, here is a randomly selected fanfiction:\n"
#         response_text += f"- {recommended_fanfic.title} by {recommended_fanfic.author} ({recommended_fanfic.url})\n"
#
#         return response_text, recommended_fanfic
#
#     except Exception as e:
#         print(f"Error selecting random fanfic: {e}")
#         return "Error selecting random fanfic", None

def recommend_fanfic(user_input, tfidf_vectorizer, fanfics, min_similarity=0.05, batch_size=10):
    # Load PCA model
    with open('pca_model.pkl', 'rb') as f:
        pca = pickle.load(f)

    # Convert user input to vector
    user_vector = tfidf_vectorizer.transform([user_input]).toarray()

    # Reduce dimensions with PCA
    user_vector_reduced = pca.transform(user_vector)

    # Initialize tracking variables
    max_similarity = -1
    recommended_fanfic = None
    found_similar_fanfic = False

    # Iterate over paginated fanfics
    page_number = 1
    while True:
        fanfics_page = fanfics.items  # Get fanfics for current page
        num_fanfics = len(fanfics_page)  # Number of fanfics in the current page

        # Batch processing
        for start in range(0, num_fanfics, batch_size):
            end = min(start + batch_size, num_fanfics)
            batch_fanfics = fanfics_page[start:end]

            try:
                # Batch vectors and indices
                batch_vectors = []
                batch_indices = []

                for fanfic in batch_fanfics:
                    fanfic_vector = np.array(fanfic.vector)
                    if fanfic_vector is None:
                        continue
                    batch_vectors.append(fanfic_vector)
                    batch_indices.append(fanfic.index)

                if not batch_vectors:
                    continue

                # Compute cosine similarities for the batch
                similarities = cosine_similarity(user_vector_reduced, batch_vectors)

                # Find the best match in the batch
                max_batch_index = np.argmax(similarities)
                max_batch_similarity = similarities[0, max_batch_index]

                # Log the best similarity value after each batch
                print(
                    f"Best similarity after batch {start // batch_size + 1} on page {page_number}: {max_batch_similarity}")

                # Check if similarity meets the minimum threshold
                if max_batch_similarity >= min_similarity:
                    recommended_fanfic = batch_fanfics[max_batch_index]
                    found_similar_fanfic = True
                    break

                # Track the most similar fanfic overall
                if max_batch_similarity > max_similarity:
                    max_similarity = max_batch_similarity
                    recommended_fanfic = batch_fanfics[max_batch_index]

            except Exception as e:
                print(f"Error processing batch from {start} to {end} on page {page_number}: {e}")
                continue

            finally:
                # Clean up memory after each batch
                del batch_vectors, batch_indices
                gc.collect()

        # Move to the next page if available
        if not fanfics.has_next:
            break
        fanfics = fanfics.next()  # Move to the next page
        page_number += 1

    if found_similar_fanfic:
        response_text = f"User: {user_input}\nAI: Based on your interest, here is a fanfiction recommendation:\n"
        response_text += f"- {recommended_fanfic.title} by {recommended_fanfic.author} ({recommended_fanfic.url})\n"
    else:
        response_text = "No similar fanfics found. Here is the most similar fanfic available:\n"
        if recommended_fanfic:
            response_text += f"- {recommended_fanfic.title} by {recommended_fanfic.author} ({recommended_fanfic.url})\n"
        else:
            response_text += "No fanfics available."

    return response_text, recommended_fanfic





# Worked prior, with DOCKER
# def recommend_fanfic(user_input, tfidf_vectorizer, fanfics, batch_size=1000):
#     # Load PCA model
#     with open('pca_model.pkl', 'rb') as f:
#         pca = pickle.load(f)
#
#     # Convert user input to vector
#     user_vector = tfidf_vectorizer.transform([user_input]).toarray()
#
#     # Reduce dimensions with PCA
#     user_vector_reduced = pca.transform(user_vector)
#
#     # Initialize tracking variables
#     max_similarity = -1
#     recommended_fanfic = None
#
#     # Batch processing
#     num_fanfics = len(fanfics)
#     for start in range(0, num_fanfics, batch_size):
#         end = min(start + batch_size, num_fanfics)
#         batch_vectors = np.array([fanfic.vector for fanfic in fanfics[start:end]])  # Assuming fanfic.vector is already a list or numpy array
#
#         try:
#             # Compute cosine similarity for the batch
#             similarities = cosine_similarity(user_vector_reduced, batch_vectors)
#
#             # Find the best match in the current batch
#             max_batch_index = np.argmax(similarities)
#             max_batch_similarity = similarities[0, max_batch_index]  # Use [0, max_batch_index] because similarities is 2D
#
#             if max_batch_similarity > max_similarity:
#                 max_similarity = max_batch_similarity
#                 recommended_fanfic = fanfics[start + max_batch_index]
#
#         except Exception as e:
#             print(f"Error processing batch from {start} to {end}: {e}")
#             continue
#
#         finally:
#             # Clean up memory after each batch
#             del batch_vectors
#             gc.collect()  # Force garbage collection to free up memory
#
#     if recommended_fanfic:
#         response_text = f"User: {user_input}\nAI: Based on your interest, here are some fanfiction recommendations:\n"
#         response_text += f"- {recommended_fanfic.title} by {recommended_fanfic.author} ({recommended_fanfic.url})\n"
#     else:
#         response_text = "No recommendations found."
#
#     return response_text, recommended_fanfic