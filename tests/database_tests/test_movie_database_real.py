import json
import os
import unittest

from tests.database_tests.abstract_movie_database_test import AbstractMovieDatabaseTest


class TestMovieDatabaseReal(AbstractMovieDatabaseTest):
    @unittest.skip
    def test_0_update_real_data(self) -> None:
        movies = self.movie_database.kinopoisk_parser.parse_movies(movie_ids=[389])
        with open(os.path.join(self.data_path, "real", "movie.json"), "w", encoding="utf-8") as f:
            json.dump({"movies": movies}, f, ensure_ascii=False)

        movies = self.movie_database.kinopoisk_parser.parse_movies(movie_ids=[14288, 775276, 493208])
        with open(os.path.join(self.data_path, "real", "movie_and_cartoon.json"), "w", encoding="utf-8") as f:
            json.dump({"movies": movies}, f, ensure_ascii=False)

    def test_1_insert_movie(self) -> None:
        self.add_from_kinopoisk("real/movie.json")
        self.assertEqual(self.movie_database.get_movies_count(), 1)
        self.assertEqual(self.movie_database.get_persons_count(), 51)

        person = self.movie_database.get_person(person_id=1)
        self.assertIsNotNone(person)
        self.assertEqual(person.name, "Жан Рено")

        movie = self.movie_database.get_movie(movie_id=1)
        self.assertIsNotNone(movie)
        self.assertEqual(movie.name, "Леон")
        self.assertEqual(movie.actors[0].person_id, 1)
        self.assertEqual(movie.actors[0].description, "Leon")

        director = self.movie_database.get_person(person_id=movie.directors[0].person_id)
        self.assertIsNotNone(director)
        self.assertEqual(director.name, "Люк Бессон")

    def test_2_insert_movie_and_cartoon(self) -> None:
        self.add_from_kinopoisk("real/movie_and_cartoon.json")
        self.assertEqual(self.movie_database.get_movies_count(), 4)
        self.assertEqual(self.movie_database.get_persons_count(), 121)

        person = self.movie_database.get_person(person_id=52)
        self.assertIsNotNone(person)
        self.assertEqual(person.name, "Рёко Хиросуэ")

        movie = self.movie_database.get_movie(movie_id=4)
        self.assertIsNotNone(movie)
        self.assertEqual(movie.name, "Холодное сердце")
