import json
import pickle

import numpy as np

class FanficRecommender:
    def __init__(self, SessionLocal):
        self.SessionLocal = SessionLocal
        # self.EmbeddingStore = EmbeddingStore

    def get_vector(self, user_input):
        with open('pca_model.pkl', 'rb') as f:
            pca = pickle.load(f)

        with open('tfidf_vectorizer.pkl', 'rb') as f:
            tfidf_vectorizer = pickle.load(f)

        # Convert user input to vector & reduce dimensions
        user_vector = tfidf_vectorizer.transform([user_input])
        user_vector_reduced = pca.transform(user_vector)
        return user_vector_reduced

    def cosine_similarity(self, vec1, vec2):
        dot_product = np.dot(vec1, vec2)
        norm_vec1 = np.linalg.norm(vec1)
        norm_vec2 = np.linalg.norm(vec2)
        return dot_product / (norm_vec1 * norm_vec2)

    def custom_similarity_search_with_scores(self, query, supabase):
        query_vector = self.get_vector(query)

        # Fetch fanfic data from Supabase
        fanfics_data = supabase.table('fanfics_100').select('*').execute().data

        if not fanfics_data:
            raise ValueError("No fanfics found in the Supabase table.")

        # Print types for debugging
        query_vector_type = type(query_vector)
        fanfic_vector_type = type(fanfics_data[0]['vector'])

        # Check types
        if query_vector_type != fanfic_vector_type:
            if fanfic_vector_type == str:
                try:
                    fanfics_data = [
                        {**fanfic, 'vector': np.array(json.loads(fanfic['vector']))}
                        for fanfic in fanfics_data
                    ]
                except json.JSONDecodeError as e:
                    raise TypeError(
                        f"Type mismatch: query_vector is of type {query_vector_type}, but fanfic['vector'] could not be converted to a NumPy array: {str(e)}"
                    )
            else:
                raise TypeError(
                    f"Type mismatch: query_vector is of type {query_vector_type}, but fanfic['vector'] is of type {fanfic_vector_type}"
                )

        # Compute cosine similarity and store (id, similarity) tuples
        similarities = [(fanfic['id'], self.cosine_similarity(query_vector, fanfic['vector']))
                        for fanfic in fanfics_data]

        if not similarities:
            raise ValueError("No similarities computed from the Supabase results.")

        # Find the best match (highest similarity)
        best_match = max(similarities, key=lambda x: x[1])

        return best_match[0]  # Return the ID of the best match
