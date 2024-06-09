import os
import random
import traceback

from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import csv
from tenacity import retry, stop_after_delay, wait_fixed
from flask_talisman import Talisman
import logging
from sqlalchemy.dialects.postgresql.base import PGDialect

def create_app():
    # Override the _get_server_version_info method
    PGDialect._get_server_version_info = lambda *args: (9, 2)

    app = Flask(__name__)
    CORS(app)  # Enable CORS for all routes

    # Configure the SQLAlchemy database URI using environment variables
    # db_user = os.getenv('DB_USER')
    # db_password = os.getenv('DB_PASSWORD')
    # db_host = os.getenv('DB_HOST')
    # db_port = os.getenv('DB_PORT')
    # db_name = os.getenv('DB_NAME')

    db_uri = os.getenv('DATABASE_URI')  # Use the provided PostgreSQL URI

    # Initialize the SQLAlchemy database
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db = SQLAlchemy(app)

    # Define the database model
    class Fanfic(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        index = db.Column(db.Integer)
        title = db.Column(db.String(255))
        author = db.Column(db.String(255))
        fandom = db.Column(db.String(255))
        url = db.Column(db.String(255))
        kudos = db.Column(db.String(255))
        average_sentiment = db.Column(db.Float)

        def __repr__(self):
            return f"<Fanfic {self.title}>"

    # Load data from CSV file into the database
    def load_data_from_csv(csv_file):
        with open(csv_file, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                fanfic = Fanfic(
                    index=int(row['ID']),
                    title=row['Title'],
                    author=row['Author'],
                    fandom=row['Fandom'],
                    url=row['Url'],
                    kudos=row['Kudos'],
                    average_sentiment=float(row['Average_Sentiment'])
                )
                db.session.add(fanfic)
            db.session.commit()

    # Method to randomly select a fanfic
    @retry(stop=stop_after_delay(30), wait=wait_fixed(5))
    def get_random_fanfic():
        random_index = random.randint(0, 2826)
        return Fanfic.query.filter_by(index=random_index).first()

    @app.route('/random_fanfic', methods=['GET'])
    def random_fanfic():
        try:
            fanfic = get_random_fanfic()
            if fanfic:
                return jsonify({'title': fanfic.title, 'author': fanfic.author, 'fandom': fanfic.fandom, 'url': fanfic.url, 'kudos': fanfic.kudos, 'average_sentiment': fanfic.average_sentiment})
            else:
                return jsonify({'error': 'No fanfics found'}), 404
        except Exception as e:
            app.logger.error('An error occurred:', exc_info=True)
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500

    @app.route('/fanfics', methods=['GET'])
    def get_fanfics():
        try:
            fanfics = Fanfic.query.all()
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

    @app.route('/')
    def index():
        return 'Hello, World!!!!'

    # Configure security headers
    talisman = Talisman(app)


    # Configure logging
    logging.basicConfig(filename='app.log', level=logging.INFO)

    # Create all tables within the application context
    with app.app_context():
        # Drop all tables (clear the database)
        # Create all tables
        db.create_all()

        if Fanfic.query.count() == 0:
            # Load data from CSV file when the app starts
            load_data_from_csv('fanfic_sentiment_analysis.csv')

    return app