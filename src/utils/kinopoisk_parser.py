import logging
import random
import time
from typing import Dict, List, Set

import requests

from src.enums import Genre, MovieType
from src.enums.production import Production


class KinopoiskParser:
    def __init__(self, tokens: List[str], logger: logging.Logger) -> None:
        self.tokens = {token: True for token in tokens}
        self.logger = logger

        self.movie_fields = [
            "id", "name", "type", "year", "slogan", "description", "shortDescription", "countries", "genres", "persons",
            "movieLength", "rating", "votes", "poster", "backdrop", "facts", "alternativeName", "names", "enName"
        ]
        self.image_types = ["screenshot", "shooting", "still"]

    def parse_movies(self, movie_ids: List[int]) -> List[dict]:
        movies = self.__get_movies(query_params=[f"id={movie_id}" for movie_id in movie_ids])
        movie_id2images = self.parse_movie_images(movie_ids=movie_ids)
        return [self.__parse_movie(movie, movie_id2images[movie["id"]]) for movie in movies]

    def parse_movie_images(self, movie_ids: List[int]) -> Dict[int, List[dict]]:
        movie_id2images = {movie_id: [] for movie_id in movie_ids}

        for image in self.__get_images(query_params=[f"movieId={movie_id}" for movie_id in movie_ids]):
            movie_id2images[image["movieId"]].append(image)

        return movie_id2images

    def __parse_movie(self, movie: dict, images: List[dict]) -> dict:
        description = movie["description"] if movie["description"] else ""
        short_description = movie["shortDescription"] if movie["shortDescription"] else ""
        countries = [country["name"] for country in movie["countries"]]

        rating = movie.get("rating", {"kp": 0, "imdb": 0})
        votes = movie.get("votes", {"kp": 0})
        backdrop = movie.get("backdrop", {"previewUrl": None})
        facts = movie.get("facts", [])

        names = {name["name"] for name in movie.get("names", [])}
        if movie.get("alternativeName", ""):
            names.add(movie["alternativeName"])

        if movie.get("enName", ""):
            names.add(movie["enName"])

        return {
            "kinopoisk_id": movie["id"],
            "name": movie["name"],
            "movie_type": MovieType.from_kinopoisk(movie["type"]).value,
            "year": movie["year"],
            "slogan": movie["slogan"] if movie["slogan"] else "",
            "description": self.__get_spoilers(text=description, names=names),
            "short_description": self.__get_spoilers(text=short_description, names=names),
            "production": [production.value for production in Production.from_countries(countries=countries)],
            "countries": countries,
            "genres": [Genre.from_kinopoisk(genre["name"]).value for genre in movie["genres"]],
            "directors": self.__filter_persons(movie["persons"], "director"),
            "actors": self.__filter_persons(movie["persons"], "actor"),
            "duration": movie["movieLength"],
            "rating": {"rating_kp": rating.get("kp", 0), "rating_imdb": rating.get("imdb", 0), "votes_kp": votes.get("kp", 0)},
            "image_urls": [image["url"] for image in images if image["width"] >= image["height"] * 1.3],
            "poster_url": movie["poster"]["previewUrl"],
            "banner_url": backdrop["previewUrl"],
            "facts": [self.__get_spoilers(text=fact["value"], names=names) for fact in facts] if facts else [],
            "alternative_names": sorted(names)
        }

    def __filter_persons(self, persons: List[dict], profession: str) -> List[dict]:
        filtered = []

        for person in persons:
            if person["enProfession"] != profession:
                continue

            filtered.append({
                "kinopoisk_id": person["id"],
                "name": person["name"],
                "photo_url": person["photo"],
                "description": person["description"] if person["description"] else ""
            })

        return filtered

    def __get_spoilers(self, text: str, names: Set[str]) -> dict:
        return {"text": text, "spoilers": []}  # TODO

    def __get_movies(self, query_params: List[str]) -> List[dict]:
        params = ["limit=250", *[f"selectFields={field}" for field in self.movie_fields], *query_params]
        return self.__list_request(url=f'/v1.4/movie?{"&".join(params)}', target="movies")

    def __get_images(self, query_params: List[str]) -> List[dict]:
        params = ["limit=250", *[f"type={image_type}" for image_type in self.image_types], *query_params]
        return self.__list_request(url=f'/v1.4/image?{"&".join(params)}', target="images")

    def __list_request(self, url: str, target: str) -> List[dict]:
        response = self.__api_request(url)
        docs = response["docs"]
        self.logger.info(f'{target}: {response["pages"]} pages')

        while response["page"] < response["pages"]:
            self.logger.info(f'{target}: {response["page"] + 1} / {response["pages"]}')
            response = self.__api_request(f'{url}&page={response["page"] + 1}')
            docs.extend(response["docs"])

        return docs

    def __api_request(self, url: str) -> dict:
        while True:
            token = self.__get_token()
            response = requests.get(f"https://api.kinopoisk.dev{url}", headers={
                "accept": "application/json",
                "X-API-KEY": token
            })

            if response.status_code == 200:
                return response.json()

            if response.status_code == 403:
                self.tokens[token] = False
                self.logger.warning(f"WARNING! 403 error ({response.text})")
                continue

            time.sleep(5)
            self.logger.warning(f"WARNING! {response.status_code} error ({response.text})")

    def __get_token(self) -> str:
        while True:
            if available_tokens := [token for token, is_available in self.tokens.items() if is_available]:
                return random.choice(available_tokens)

            self.logger.warning("WARNING! no available tokens")

            for token in self.tokens:
                self.tokens[token] = True

            time.sleep(10)
