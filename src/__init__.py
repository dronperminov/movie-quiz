import json
import logging
import os
import sys

from src.database import Database
from src.movie_database import MovieDatabase
from src.questions_database import QuestionsDatabase
from src.quiz_tours_database import QuizToursDatabase
from src.utils.kinopoisk_parser import KinopoiskParser


logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger()

secrets_path = os.path.join(os.path.dirname(__file__), "..", "secrets.json")

if os.path.exists(secrets_path):
    with open(secrets_path, "r") as f:
        secrets = json.load(f)
    kinopoisk_parser = KinopoiskParser(tokens=secrets["kinopoisk_tokens"], logger=logger)
else:
    kinopoisk_parser = None

database = Database(mongo_url="mongodb://localhost:27017/", database_name="movie_quiz_db")
movie_database = MovieDatabase(database=database, kinopoisk_parser=kinopoisk_parser, logger=logger)
questions_database = QuestionsDatabase(database=database, movie_database=movie_database, logger=logger)
quiz_tours_database = QuizToursDatabase(database=database, questions_database=questions_database, logger=logger)
