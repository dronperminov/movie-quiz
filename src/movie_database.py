import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from urllib.error import HTTPError, URLError

import wget

from src import Database
from src.entities.history_action import AddMovieAction, AddPersonAction, EditMovieAction, EditPersonAction, RemoveMovieAction, RemovePersonAction
from src.entities.metadata import Metadata
from src.entities.movie import Movie
from src.entities.person import Person
from src.entities.source import KinopoiskSource
from src.query_params.movie_search import MovieSearch
from src.query_params.person_movies import PersonMovies
from src.utils.images import resize_image
from src.utils.kinopoisk_parser import KinopoiskParser


class MovieDatabase:
    def __init__(self, database: Database, kinopoisk_parser: KinopoiskParser, logger: logging.Logger) -> None:
        self.database = database
        self.kinopoisk_parser = kinopoisk_parser
        self.logger = logger

    def get_movies_count(self) -> int:
        return self.database.movies.count_documents({})

    def get_movie(self, movie_id: int) -> Optional[Movie]:
        movie = self.database.movies.find_one({"movie_id": movie_id})
        return Movie.from_dict(movie) if movie else None

    def get_movies_persons(self, movies: List[Movie]) -> Dict[int, Person]:
        person_ids = [actor.person_id for movie in movies for actor in movie.actors + movie.directors]
        persons = self.database.persons.find({"person_id": {"$in": person_ids}})
        return {person["person_id"]: Person.from_dict(person) for person in persons}

    def get_last_movies(self, order_field: str, order_type: int, count: int) -> List[Movie]:
        _, movies = self.search_movies(MovieSearch(order_type=order_type, order=order_field, page_size=count, page=0))
        return movies

    def search_movies(self, params: MovieSearch) -> Tuple[int, List[Movie]]:
        results = self.database.movies.aggregate([
            {
                "$addFields": {
                    "name_lowercase": {"$replaceAll": {"input": {"$toLower": "$name"}, "find": "Ё", "replacement": "Е"}}
                }
            },
            {"$match": params.to_query()},
            {"$sort": {params.order: params.order_type, "_id": 1}},
            {
                "$facet": {
                    "movies": [{"$skip": params.page_size * params.page}, {"$limit": params.page_size}],
                    "total": [{"$count": "count"}]
                }
            }
        ])

        results = list(results)[0]
        total = 0 if not results["total"] else results["total"][0]["count"]
        return total, [Movie.from_dict(movie) for movie in results["movies"]]

    def download_movie_images(self, output_path: str, username: str) -> None:
        query = {
            "$or": [
                {"image_urls": {"$ne": [], "$not": {"$regex": "^/images/movie_images/.*"}}},
                {"banner_url": {"$not": {"$regex": "^/images/movie_banners/.*"}}},
                {"poster_url": {"$not": {"$regex": "^/images/movie_posters/.*"}}}
            ]
        }

        for movie in self.database.movies.find(query):
            movie = Movie.from_dict(movie)

            image_urls = [image_url for image_url in movie.image_urls]
            banner_url = movie.banner_url
            poster_url = movie.poster_url

            if banner_url and not banner_url.startswith("/images/movie_banners/"):
                try:
                    self.__download_kinopoisk_image(banner_url, os.path.join(output_path, "movie_banners", f"{movie.movie_id}.webp"), max_width=1000)
                    banner_url = f"/images/movie_banners/{movie.movie_id}.webp"
                except ValueError:
                    self.logger.error(f'Unable to download movie banner "{movie.movie_id}"')

            if poster_url and not poster_url.startswith("/images/movie_posters/"):
                try:
                    self.__download_kinopoisk_image(poster_url, os.path.join(output_path, "movie_posters", f"{movie.movie_id}.webp"), max_width=128)
                    poster_url = f"/images/movie_posters/{movie.movie_id}.webp"
                except ValueError:
                    self.logger.error(f'Unable to download movie poster "{movie.movie_id}"')

            for i, image_url in enumerate(movie.image_urls):
                if not image_url.startswith("/images/movie_images"):
                    try:
                        self.__download_kinopoisk_image(image_url, os.path.join(output_path, "movie_images", f"{movie.movie_id}", f"{i + 1}.webp"), max_width=1000)
                        image_urls[i] = f"/images/movie_images/{movie.movie_id}/{i + 1}.webp"
                    except ValueError:
                        self.logger.error(f'Unable to download movie image {i + 1} "{movie.movie_id}"')

            diff = movie.get_diff({"image_urls": image_urls, "banner_url": banner_url, "poster_url": poster_url})
            self.update_movie(movie_id=movie.movie_id, diff=diff, username=username)

    def download_person_images(self, output_path: str, username: str) -> None:
        for person in self.database.persons.find({"photo_url": {"$not": {"$regex": "^/images/persons/.*"}}}):
            person = Person.from_dict(person)

            try:
                self.__download_kinopoisk_image(person.photo_url, os.path.join(output_path, "persons", f"{person.person_id}.webp"), max_width=250)
                self.update_person(person_id=person.person_id, diff=person.get_diff({"photo_url": f"/images/persons/{person.person_id}.webp"}), username=username)
            except ValueError:
                self.logger.error(f'Unable to download person photo "{person.person_id}"')

    def add_movie(self, movie: Movie, username: str) -> None:
        action = AddMovieAction(username=username, timestamp=datetime.now(), movie_id=movie.movie_id)
        self.database.movies.insert_one(movie.to_dict())
        self.database.history.insert_one(action.to_dict())
        self.logger.info(f'Added movie "{movie.name}" ({movie.movie_id}) by @{username}')

    def update_movie(self, movie_id: int, diff: dict, username: str) -> None:
        if not diff:
            return

        movie = self.database.movies.find_one({"movie_id": movie_id}, {"name": 1})
        assert movie is not None

        action = EditMovieAction(username=username, timestamp=datetime.now(), movie_id=movie_id, diff=diff)

        new_values = {key: key_diff["new"] for key, key_diff in diff.items()}
        new_values["metadata.updated_at"] = action.timestamp
        new_values["metadata.updated_by"] = action.username

        self.database.movies.update_one({"movie_id": movie_id}, {"$set": new_values})
        self.database.history.insert_one(action.to_dict())
        self.logger.info(f'Updated movie "{movie["name"]}" ({movie_id}) by @{username} (keys: {[key for key in diff]})')

    def remove_movie(self, movie_id: int, username: str) -> None:
        movie = self.database.movies.find_one({"movie_id": movie_id}, {"name": 1, "actors": 1, "directors": 1})
        assert movie is not None

        action = RemoveMovieAction(username=username, timestamp=datetime.now(), movie_id=movie_id)
        self.database.movies.delete_one({"movie_id": movie_id})

        for person in self.database.persons.find({"person_id": {"$in": [person["person_id"] for person in movie["actors"] + movie["directors"]]}}):
            if not self.database.movies.find_one({"$or": [{"actors.person_id": person["person_id"]}, {"directors.person_id": person["person_id"]}]}, {"_id": 1}):
                self.remove_person(person_id=person["person_id"], username=username)

        self.database.history.insert_one(action.to_dict())
        self.logger.info(f'Removed movie "{movie["name"]}" ({movie_id}) by @{username}')

    def get_persons_count(self) -> int:
        return self.database.persons.count_documents({})

    def get_person(self, person_id: int) -> Optional[Person]:
        person = self.database.persons.find_one({"person_id": person_id})
        return Person.from_dict(person) if person else None

    def get_person_movies(self, params: PersonMovies) -> Tuple[int, List[Movie]]:
        query = {"$or": [{"actors.person_id": params.person_id}, {"directors.person_id": params.person_id}]}
        total = self.database.movies.count_documents(query)
        movies = self.database.movies.find(query).sort({"rating.votes_kp": -1, "_id": 1}).skip(params.page * params.page_size).limit(params.page_size)
        return total, [Movie.from_dict(movie) for movie in movies]

    def add_person(self, person: Person, username: str) -> None:
        action = AddPersonAction(username=username, timestamp=datetime.now(), person_id=person.person_id)
        self.database.persons.insert_one(person.to_dict())
        self.database.history.insert_one(action.to_dict())
        self.logger.info(f'Added person "{person.name}" ({person.person_id}) by @{username}')

    def update_person(self, person_id: int, diff: dict, username: str) -> None:
        if not diff:
            return

        person = self.database.persons.find_one({"person_id": person_id}, {"name": 1})
        assert person is not None

        action = EditPersonAction(username=username, timestamp=datetime.now(), person_id=person_id, diff=diff)

        new_values = {key: key_diff["new"] for key, key_diff in diff.items()}
        new_values["metadata.updated_at"] = action.timestamp
        new_values["metadata.updated_by"] = action.username

        self.database.persons.update_one({"person_id": person_id}, {"$set": new_values})
        self.database.history.insert_one(action.to_dict())
        self.logger.info(f'Updated person "{person["name"]}" ({person_id}) by @{username} (keys: {[key for key in diff]})')

    def remove_person(self, person_id: int, username: str) -> None:
        person = self.database.persons.find_one({"person_id": person_id}, {"name": 1})
        assert person is not None

        if self.database.movies.find_one({"$or": [{"actors.person_id": person_id}, {"directors.person_id": person_id}]}):
            self.logger.error(f'Unable to remove person "{person["name"]}" ({person_id})')
            return

        action = RemovePersonAction(username=username, timestamp=datetime.now(), person_id=person_id)
        self.database.persons.delete_one({"person_id": person_id})
        self.database.history.insert_one(action.to_dict())
        self.logger.info(f'Removed person "{person["name"]}" ({person_id}) by @{username}')

    def add_from_kinopoisk(self, movies: List[dict], username: str) -> Tuple[int, int]:
        movies_count = self.get_movies_count()
        persons_count = self.get_persons_count()
        kinopoisk_id2person_id = {}

        for movie in movies:
            for person in movie["actors"] + movie["directors"]:
                kinopoisk_id2person_id[person["kinopoisk_id"]] = self.__add_kinopoisk_person(person, username=username)

            self.__add_kinopoisk_movie(kinopoisk_movie=movie, username=username, kinopoisk_id2person_id=kinopoisk_id2person_id)

        return self.get_movies_count() - movies_count, self.get_persons_count() - persons_count

    def __add_kinopoisk_person(self, kinopoisk_person: dict, username: str) -> int:
        kinopoisk_id: int = kinopoisk_person["kinopoisk_id"]

        if (person := self.database.persons.find_one({"kinopoisk_id": kinopoisk_id})) is not None:
            person = Person.from_dict(person)
            self.update_person(person_id=person.person_id, diff=person.get_diff(kinopoisk_person), username=username)
            return person.person_id

        person = Person.from_dict({
            **kinopoisk_person,
            "person_id": self.database.get_identifier("persons"),
            "metadata": Metadata.initial(username=username).to_dict()
        })

        self.add_person(person=person, username=username)
        return person.person_id

    def __add_kinopoisk_movie(self, kinopoisk_movie: dict, username: str, kinopoisk_id2person_id: Dict[int, int]) -> None:
        kinopoisk_id: int = kinopoisk_movie["kinopoisk_id"]

        actors = kinopoisk_movie.pop("actors")
        directors = kinopoisk_movie.pop("directors")
        kinopoisk_movie["actors"] = [{"person_id": kinopoisk_id2person_id[actor["kinopoisk_id"]], "description": actor["description"]} for actor in actors]
        kinopoisk_movie["directors"] = [{"person_id": kinopoisk_id2person_id[director["kinopoisk_id"]], "description": director["description"]} for director in directors]

        if (movie := self.database.movies.find_one({"source.kinopoisk_id": kinopoisk_id})) is not None:
            movie = Movie.from_dict(movie)
            self.update_movie(movie_id=movie.movie_id, diff=movie.get_diff(kinopoisk_movie), username=username)
            return

        movie = Movie.from_dict({
            **kinopoisk_movie,
            "movie_id": self.database.get_identifier("movies"),
            "source": KinopoiskSource(kinopoisk_id=kinopoisk_id).to_dict(),
            "cites": [],
            "tracks": [],
            "metadata": Metadata.initial(username=username).to_dict()
        })

        self.add_movie(movie=movie, username=username)

    def __download_kinopoisk_image(self, url: str, image_path: str, max_width: int) -> None:
        os.makedirs(os.path.dirname(image_path), exist_ok=True)

        if os.path.exists(image_path):
            os.remove(image_path)

        try:
            wget.download(url, image_path)
            resize_image(image_path, max_width=max_width)
            return
        except (FileNotFoundError, HTTPError, URLError, ValueError):
            raise ValueError("Unable to download image")
