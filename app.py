import os

import random
import traceback
from pg_vector import FanficRecommender
from supabase import create_client, Client

from flask import Flask, jsonify, request
from sqlalchemy.dialects.postgresql.base import PGDialect
from flask_cors import CORS
from tenacity import retry, stop_after_delay, wait_fixed
from flask_talisman import Talisman
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

def create_app():
    # Override the _get_server_version_info method
    PGDialect._get_server_version_info = lambda *args: (9, 2)

    app = Flask(__name__)
    CORS(app)  # Enable CORS for all routes

    # Load environment variables
    supabase_url: str = os.environ.get("SUPABASE_URL")
    supabase_key: str = os.environ.get("SUPABASE_API_KEY")
    supabase: Client = create_client(supabase_url, supabase_key)
    db_connection_string = os.getenv('SUPABASE_DB_CONNECTION')

    # Configure the SQLAlchemy part of the app instance
    app.config['SQLALCHEMY_DATABASE_URI'] = db_connection_string
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize the PgvectorService
    engine = create_engine(db_connection_string)
    SessionLocal = sessionmaker(bind=engine)
    Base = declarative_base()

    # Create the tables in the database
    Base.metadata.create_all(bind=engine)

    # Configure security headers
    # talisman = Talisman(app, content_security_policy=None, force_https=False)
    talisman = Talisman(app)

    @app.route('/', methods=['GET'])
    def index():
        return 'Hello, World!!!!'

    # Random Fanfic Feature
    @retry(stop=stop_after_delay(30), wait=wait_fixed(5))
    @app.route('/random_fanfic', methods=['GET'])
    def random_fanfic():
        try:
            random_index = random.randint(0, 6720)

            response = supabase.table("fanfics").select("*").eq("id", random_index).execute()

            if response.data is None or len(response.data) == 0:
                return jsonify({'error': 'No fanfic found'}), 404
            else:
                fanfic_data = response.data[0]
                return jsonify({
                    'title': fanfic_data.get('title', ''),
                    'author': fanfic_data.get('author', ''),
                    'url': fanfic_data.get('url', ''),
                    'fandom': fanfic_data.get('fandom', ''),
                    'kudos': fanfic_data.get('kudos', ''),
                    'average_sentiment': fanfic_data.get('average_sentiment', '')
                })
        except Exception as e:
            app.logger.error('Error fetching random fanfic:', exc_info=True)
            return jsonify({'error': str(e)}), 500

    # Pagination of Fanfics
    @retry(stop=stop_after_delay(30), wait=wait_fixed(5))
    @app.route('/fanfics', methods=['GET'])
    def get_fanfics():
        try:
            page_number = request.args.get('page', default=1, type=int)
            page_size = request.args.get('size', default=10, type=int)
            offset = (page_number - 1) * page_size

            response = supabase.table("fanfics").select("*").range(offset, offset + page_size - 1).execute()

            fanfics_data = response.data
            return jsonify(fanfics_data)

        except Exception as e:
            app.logger.error('Error fetching fanfics:', exc_info=True)
            return jsonify({'error': str(e)}), 500

    # Recommendation Fanfic Feature
    @app.route('/chat', methods=['POST'])
    def chat():
        recommender = FanficRecommender(SessionLocal)
        try:
            user_input = request.json['message']

            best_fanfic_id = recommender.custom_similarity_search_with_scores(user_input, supabase)

            response = supabase.table("fanfics").select("*").eq("id", best_fanfic_id).execute()

            if response.data is None or len(response.data) == 0:
                return jsonify({'error': 'No fanfic found'}), 404
            else:
                fanfic_data = response.data[0]
                return jsonify({
                    'title': fanfic_data.get('title', ''),
                    'author': fanfic_data.get('author', ''),
                    'url': fanfic_data.get('url', ''),
                    'fandom': fanfic_data.get('fandom', ''),
                    'kudos': fanfic_data.get('kudos', ''),
                    'average_sentiment': fanfic_data.get('average_sentiment', '')
                })

        except Exception as e:
            app.logger.error('An error occurred:', exc_info=True)
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500

    @app.route('/keep_alive', methods=['GET'])
    def keep_alive():
        return 'I am alive', 200

    return app

# if __name__ == '__main__':
#     app = create_app()
#     app.run(debug=True)
