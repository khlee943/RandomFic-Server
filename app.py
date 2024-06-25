import json
import os
import pickle
import random
import traceback

import pandas as pd
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy.exc import OperationalError, NoResultFound
from sqlalchemy import PickleType
from tenacity import retry, stop_after_delay, wait_exponential, wait_fixed
from flask_talisman import Talisman
import logging
from sqlalchemy.dialects.postgresql.base import PGDialect
from chat import recommend_fanfic

def create_app():
    # Override the _get_server_version_info method
    PGDialect._get_server_version_info = lambda *args: (9, 2)

    app = Flask(__name__)
    CORS(app)  # Enable CORS for all routes

    # Configure the SQLAlchemy database URI using environment variables; development only
    db_user = os.getenv('DB_USER', 'postgres')
    db_password = os.getenv('DB_PASSWORD')
    db_host = os.getenv('DB_HOST', 'db')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'fanfics')

    # for deployment
    # db_uri = f"postgresql://postgres:{db_password}@db:5432/fanfics"

    # for production:
    db_uri = os.getenv('DATABASE_URI')  # Use the provided PostgreSQL URI

    # Initialize the SQLAlchemy database
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db = SQLAlchemy(app)

    with open('tfidf_vectorizer.pkl', 'rb') as f:
        tfidf_vectorizer = pickle.load(f)

    # Define the database model
    class Fanfic(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        index = db.Column(db.Integer)
        title = db.Column(db.String(255))
        author = db.Column(db.String(255))
        fandom = db.Column(db.String(500))
        url = db.Column(db.String(255))
        kudos = db.Column(db.String(255))
        average_sentiment = db.Column(db.Float)
        vector = db.Column(PickleType)

        def __repr__(self):
            return f"<Fanfic {self.title}>"

    # Random Fanfic Feature

    def safe_json_loads(x):
        try:
            return json.loads(x)
        except (json.JSONDecodeError, TypeError):
            return None  # Handle the error as appropriate, e.g., logging the error

    # Load all fanfic info data from CSV file into the database
    @retry(wait=wait_exponential(multiplier=1, max=10), stop=stop_after_delay(50))
    def insert_fanfic_data(chunk):
        chunk['Vector'] = chunk['Vector'].apply(safe_json_loads)

        batch_size = 100
        batch_counter = 0

        for index, row in chunk.iterrows():
            try:
                # Truncate `fandom` if length exceeds 500 characters
                fandom_adjusted = row['Fandom']
                if len(fandom_adjusted) > 500:
                    fandom_adjusted = f"{fandom_adjusted[:497]}..."

                fanfic = Fanfic(
                    index=int(row['ID']),
                    title=row['Title'],
                    author=row['Author'],
                    fandom=fandom_adjusted,
                    url=row['Url'],
                    kudos=row['Kudos'],
                    average_sentiment=float(row['Average_Sentiment']),
                    vector=row['Vector']  # Assuming 'Vector' is a column containing JSON data
                )
                db.session.add(fanfic)
                batch_counter += 1

                # Commit every batch_size rows
                if batch_counter >= batch_size:
                    db.session.commit()
                    batch_counter = 0
            except Exception as e:
                print(f"Error inserting row with ID {row['ID']}: {e}")
                print(f"Row data: {row}")
                db.session.rollback()
                continue

        # Final commit for any remaining rows in the last batch
        if batch_counter > 0:
            db.session.commit()

        print(f"Processed {len(chunk)} rows.")
        del chunk

    def load_data_from_csv(csv_file):
        data_chunks = pd.read_csv(csv_file, chunksize=1000)

        for chunk in data_chunks:
            try:
                insert_fanfic_data(chunk)
            except OperationalError as e:
                print(f"OperationalError: {e}")
                db.session.rollback()  # Rollback the session on error
                continue
            except Exception as e:
                print(f"Error processing chunk: {e}")
                db.session.rollback()  # Rollback the session on error
                continue

    # @retry(wait=wait_exponential(multiplier=1, max=10), stop=stop_after_delay(50))
    # def insert_fanfic_data(chunk):
    #     global tfidf_vectorizer_full  # Ensure tfidf_vectorizer_full is defined globally
    #     chunk['Vector'] = chunk['Vector'].apply(safe_json_loads)
    #
    #     for index, row in chunk.iterrows():
    #         try:
    #             # Truncate `fandom` if length exceeds 500 characters
    #             fandom_adjusted = row['Fandom']
    #             if len(fandom_adjusted) > 500:
    #                 fandom_adjusted = f"{fandom_adjusted[:497]}..."
    #
    #             fanfic = Fanfic(
    #                 index=int(row['ID']),
    #                 title=row['Title'],
    #                 author=row['Author'],
    #                 fandom=fandom_adjusted,
    #                 url=row['Url'],
    #                 kudos=row['Kudos'],
    #                 average_sentiment=float(row['Average_Sentiment']),
    #                 vector=row['Vector']  # Assuming 'Vector' is a column containing JSON data
    #             )
    #             db.session.add(fanfic)
    #         except Exception as e:
    #             print(f"Error inserting row with ID {row['ID']}: {e}")
    #             print(f"Row data: {row}")
    #             continue
    #
    #     db.session.commit()  # Commit after each chunk to avoid excessive memory usage
    #     print(f"Processed {len(chunk)} rows.")
    #     del chunk
    #
    # def load_data_from_csv(csv_file):
    #     global tfidf_vectorizer_full
    #     data_chunks = pd.read_csv(csv_file, chunksize=1000)
    #
    #     for chunk in data_chunks:
    #         try:
    #             insert_fanfic_data(chunk)
    #         except OperationalError as e:
    #             print(f"OperationalError: {e}")
    #             # You can log or handle the error as needed; retry decorator will retry up to stop_max_attempt_number times
    #             continue
    #         except Exception as e:
    #             print(f"Error processing chunk: {e}")
    #             # Handle other exceptions here if needed
    #             continue

    # Method to randomly select a fanfic
    @retry(stop=stop_after_delay(30), wait=wait_fixed(5))
    def get_random_fanfic():
        random_index = random.randint(0, 2826)
        return Fanfic.query.filter_by(index=random_index).first()

    @retry(stop=stop_after_delay(30), wait=wait_fixed(5))
    def paginate_fanfics(page_number=1, page_size=10):
        with app.app_context():
            fanfics_paginated = Fanfic.query.paginate(page=page_number, per_page=page_size, error_out=False)
        return fanfics_paginated

    # Get the formatted fanfics, paged
    global fanfics_pagination
    fanfics_pagination = paginate_fanfics()

    @app.route('/random_fanfic', methods=['GET'])
    def random_fanfic():
        try:
            fanfic = get_random_fanfic()
            if fanfic:
                return jsonify(
                    {'title': fanfic.title, 'author': fanfic.author, 'fandom': fanfic.fandom, 'url': fanfic.url,
                     'kudos': fanfic.kudos, 'average_sentiment': fanfic.average_sentiment})
            else:
                return jsonify({'error': 'No fanfics found'}), 404
        except Exception as e:
            app.logger.error('An error occurred:', exc_info=True)
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500

    @app.route('/fanfics', methods=['GET'])
    def get_fanfics():
        try:
            global fanfics_pagination
            fanfics = fanfics_pagination.items
            fanfic_list = []
            for fanfic in fanfics:
                fanfic_data = {
                    'index': fanfic.index,
                    'title': fanfic.title,
                    'author': fanfic.author,
                    'fandom': fanfic.fandom,
                    'url': fanfic.url,
                    'kudos': fanfic.kudos,
                    'average_sentiment': fanfic.average_sentiment
                }
                fanfic_list.append(fanfic_data)
            return jsonify(fanfic_list)
        except Exception as e:
            app.logger.error('An error occurred:', exc_info=True)
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500

    # Recommendation Fanfic Feature

    @app.route('/chat', methods=['POST'])
    def chat(fanfics):
        try:
            user_input = request.json['message']
            # fanfics = Fanfic.query.all()
            global fanfics_pagination
            response_text, recommended_fanfic = recommend_fanfic(user_input, tfidf_vectorizer, fanfics_pagination)

            response = {
                'title': recommended_fanfic.title,
                'author': recommended_fanfic.author,
                'url': recommended_fanfic.url,
                'fandom': recommended_fanfic.fandom,
                'kudos': recommended_fanfic.kudos,
                'average_sentiment': recommended_fanfic.average_sentiment,
                'response_text': response_text
            }

            return jsonify({"response": response})

        except KeyError as e:
            error_message = f"KeyError: {str(e)}"
            app.logger.error(error_message)
            return jsonify({'error': error_message}), 400  # Bad request

        except NoResultFound as e:
            error_message = "No result found in database query."
            app.logger.error(error_message)
            return jsonify({'error': error_message}), 404  # Not found

        except Exception as e:
            error_message = f"An unexpected error occurred: {str(e)}"
            app.logger.error(error_message)
            traceback.print_exc()  # Print traceback for debugging
            return jsonify({'error': error_message}), 500  # Internal server error

    @app.route('/')
    def index():
        return 'Hello, World!!!!'

    # Configure security headers
    # talisman = Talisman(app, content_security_policy=None, force_https=False)
    talisman = Talisman(app)


    # Configure logging
    logging.basicConfig(filename='app.log', level=logging.INFO)

    # Create all tables within the application context
    with app.app_context():
        db.create_all()

        # Load data from CSV file when the app starts
        load_data_from_csv('fanfic_sentiment_analysis.csv')

    return app

# # running for development
# if __name__ == '__main__':
#     app = create_app()
#     # app.run(host='0.0.0.0', port=5000, debug=True)
#     app.run(debug=True)