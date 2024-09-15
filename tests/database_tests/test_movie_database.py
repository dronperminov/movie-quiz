from tests.database_tests.abstract_movie_database_test import AbstractMovieDatabaseTest


class TestMovieDatabaseReal(AbstractMovieDatabaseTest):
    def test_1_insert_movie(self) -> None:
        self.add_from_kinopoisk("movie_insert.json")
        self.assertEqual(self.movie_database.get_movies_count(), 1)
        self.assertEqual(self.movie_database.get_persons_count(), 4)

        person = self.movie_database.get_person(person_id=1)
        self.assertIsNotNone(person)
        self.assertEqual(person.name, "Actor 1")

        movie = self.movie_database.get_movie(movie_id=1)
        self.assertIsNotNone(movie)
        self.assertEqual(movie.name, "Name 123")
        self.assertEqual(movie.year, 2024)
        self.assertEqual(movie.actors[0].person_id, 1)
        self.assertEqual(movie.actors[0].description, "Actor 1 123")

        director = self.movie_database.get_person(person_id=movie.directors[0].person_id)
        self.assertIsNotNone(director)
        self.assertEqual(director.name, "Director 1")

    def test_2_update_movie(self) -> None:
        self.add_from_kinopoisk("movie_update.json")
        self.assertEqual(self.movie_database.get_movies_count(), 1)
        self.assertEqual(self.movie_database.get_persons_count(), 4)

        movie = self.movie_database.get_movie(movie_id=1)
        self.assertIsNotNone(movie)
        self.assertEqual(movie.name, "Name 1234")
        self.assertEqual(movie.year, 2020)
        self.assertEqual(movie.actors[0].person_id, 1)
        self.assertEqual(movie.actors[0].description, "Actor 1 1234")

        director = self.movie_database.get_person(person_id=movie.directors[0].person_id)
        self.assertIsNotNone(director)
        self.assertEqual(director.name, "Director 1")

    def test_3_update_and_insert_movie(self) -> None:
        self.add_from_kinopoisk("movie_update_and_insert.json")
        self.assertEqual(self.movie_database.get_movies_count(), 2)
        self.assertEqual(self.movie_database.get_persons_count(), 5)

        movie = self.movie_database.get_movie(movie_id=1)
        self.assertIsNotNone(movie)
        self.assertEqual(movie.name, "Name 1234")
        self.assertEqual(movie.slogan, "Slogan 1234")
        self.assertEqual(movie.actors[0].person_id, 1)
        self.assertEqual(movie.actors[0].description, "Actor 1 1234")

        movie = self.movie_database.get_movie(movie_id=2)
        self.assertIsNotNone(movie)
        self.assertEqual(movie.name, "Name 666")
        self.assertEqual(movie.slogan, "Slogan 666")
        self.assertEqual(movie.actors[1].person_id, 5)
        self.assertEqual(movie.actors[1].description, "Actor 2 666")

        director = self.movie_database.get_person(person_id=movie.directors[0].person_id)
        self.assertIsNotNone(director)
        self.assertEqual(director.name, "Director 1")

        person = self.movie_database.get_person(person_id=2)
        self.assertIsNotNone(person)
        self.assertEqual(person.name, "Actor 22")
