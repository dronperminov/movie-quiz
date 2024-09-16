import os
from tempfile import TemporaryDirectory

from tests.database_tests.abstract_movie_database_test import AbstractMovieDatabaseTest


class TestMovieDatabaseDownload(AbstractMovieDatabaseTest):
    movies_count = 1
    images_count = 5
    persons_count = 26

    def test_0_init_database(self) -> None:
        movies = self.movie_database.kinopoisk_parser.parse_movies(movie_ids=[1402937], max_images=self.images_count)

        self.movie_database.add_from_kinopoisk(movies=movies, username="user")
        self.assertEqual(self.movie_database.get_movies_count(), self.movies_count)
        self.assertEqual(self.movie_database.get_persons_count(), self.persons_count)

        movie = self.movie_database.get_movie(movie_id=1)
        self.assertEqual(len(movie.image_urls), self.images_count)
        self.assertIsNotNone(movie.banner_url)
        self.assertIsNotNone(movie.poster_url)

    def test_1_download_persons(self) -> None:
        with TemporaryDirectory() as dir_name:
            self.assertEqual(len(os.listdir(dir_name)), 0)
            self.movie_database.download_person_images(output_path=dir_name, username="user")
            filenames = os.listdir(os.path.join(dir_name, "persons"))

        self.assertEqual(len(filenames), self.persons_count)

        for person_id in range(1, self.persons_count + 1):
            person = self.movie_database.get_person(person_id=person_id)
            self.assertIn(f"{person_id}.webp", filenames)
            self.assertEqual(person.photo_url, f"/images/persons/{person_id}.webp")

    def test_2_download_movies(self) -> None:
        with TemporaryDirectory() as dir_name:
            self.assertEqual(len(os.listdir(dir_name)), 0)
            self.movie_database.download_movie_images(output_path=dir_name, username="user")
            movie_images_filenames = os.listdir(os.path.join(dir_name, "movie_images", "1"))
            movie_banners_filenames = os.listdir(os.path.join(dir_name, "movie_banners"))
            movie_posters_filenames = os.listdir(os.path.join(dir_name, "movie_posters"))

        self.assertEqual(len(movie_images_filenames), self.images_count)
        self.assertEqual(len(movie_banners_filenames), self.movies_count)
        self.assertEqual(len(movie_posters_filenames), self.movies_count)

        for movie_id in range(1, self.movies_count + 1):
            movie = self.movie_database.get_movie(movie_id=movie_id)
            self.assertIn(f"{movie_id}.webp", movie_banners_filenames)
            self.assertIn(f"{movie_id}.webp", movie_posters_filenames)
            self.assertEqual(movie.banner_url, f"/images/movie_banners/{movie_id}.webp")
            self.assertEqual(movie.poster_url, f"/images/movie_posters/{movie_id}.webp")

            for i in range(self.images_count):
                self.assertIn(f"{i + 1}.webp", movie_images_filenames)
                self.assertEqual(movie.image_urls[i], f"/images/movie_images/{movie_id}/{i + 1}.webp")
