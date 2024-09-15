import json
import os
from unittest import TestCase

from src import Database, kinopoisk_parser, logger
from src.movie_database import MovieDatabase


class AbstractMovieDatabaseTest(TestCase):
    database: Database
    movie_database: MovieDatabase
    data_path = os.path.join(os.path.dirname(__file__), "..", "data")

    @classmethod
    def setUpClass(cls: "AbstractMovieDatabaseTest") -> None:
        cls.database = Database("mongodb://localhost:27017/", database_name="test_movie_quiz_db")
        cls.database.connect()
        cls.movie_database = MovieDatabase(database=cls.database, kinopoisk_parser=kinopoisk_parser, logger=logger)

    def add_from_kinopoisk(self, filename: str) -> None:
        with open(os.path.join(self.data_path, filename), encoding="utf-8") as f:
            data = json.load(f)

        self.movie_database.add_from_kinopoisk(movies=data["movies"], username="user")

    def tearDown(self) -> None:
        # TODO: self.movie_database.validate()
        pass

    @classmethod
    def tearDownClass(cls: "AbstractMovieDatabaseTest") -> None:
        cls.database.drop()
        cls.database.close()
