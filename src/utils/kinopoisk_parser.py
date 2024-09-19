import logging
import random
import re
import time
from typing import Dict, List, Set, Tuple

import requests
from Levenshtein import ratio
from bs4 import BeautifulSoup

from src.enums import Genre, MovieType, Production


class KinopoiskParser:
    def __init__(self, tokens: List[str], logger: logging.Logger) -> None:
        self.tokens = {token: True for token in tokens}
        self.logger = logger

        self.movie_fields = [
            "id", "name", "type", "year", "slogan", "description", "shortDescription", "countries", "genres", "persons",
            "movieLength", "rating", "votes", "poster", "backdrop", "facts", "alternativeName", "names", "enName"
        ]
        self.image_types = ["screenshot", "still"]

    def parse_movies(self, movie_ids: List[int], max_images: int = 50) -> List[dict]:
        movies = self.__get_movies(query_params=[f"id={movie_id}" for movie_id in movie_ids])
        movie_id2images = self.parse_movie_images(movie_ids=movie_ids)
        return [self.__parse_movie(movie, movie_id2images[movie["id"]][:max_images]) for movie in movies]

    def parse_movie_images(self, movie_ids: List[int]) -> Dict[int, List[dict]]:
        movie_id2images = {movie_id: [] for movie_id in movie_ids}

        for image in self.__get_images(query_params=[f"movieId={movie_id}" for movie_id in movie_ids]):
            if image["width"] > image["height"]:
                movie_id2images[image["movieId"]].append(image)

        return movie_id2images

    def parse_sequels(self, movie_ids: List[int]) -> Dict[int, List[dict]]:
        params = ["limit=250", "selectFields=id", "selectFields=sequelsAndPrequels", *[f"id={movie_id}" for movie_id in movie_ids]]
        movies = self.__list_request(url=f'/v1.4/movie?{"&".join(params)}', target="sequels")
        sequels = {movie_id: [] for movie_id in movie_ids}

        for movie in movies:
            sequels[movie["id"]] = movie.get("sequelsAndPrequels", [])
        return sequels

    def __parse_movie(self, movie: dict, images: List[dict]) -> dict:
        description = self.__clear_spaces(movie["description"]) if movie["description"] else ""
        short_description = self.__clear_spaces(movie["shortDescription"]) if movie["shortDescription"] else ""
        countries = [country["name"] for country in movie["countries"]]

        rating = movie.get("rating", {"kp": 0, "imdb": 0})
        votes = movie.get("votes", {"kp": 0})
        backdrop = movie.get("backdrop", {"url": None})
        facts = movie.get("facts", [])

        names = {self.__clear_spaces(name["name"]) for name in movie.get("names", [])}
        if movie.get("alternativeName", ""):
            names.add(self.__clear_spaces(movie["alternativeName"]))

        if movie.get("enName", ""):
            names.add(self.__clear_spaces(movie["enName"]))

        return {
            "kinopoisk_id": movie["id"],
            "name": self.__clear_spaces(movie["name"]),
            "movie_type": MovieType.from_kinopoisk(movie["type"]).value,
            "year": movie["year"],
            "slogan": self.__clear_spaces(movie["slogan"]) if movie["slogan"] else "",
            "description": self.__get_spoilers(text=description, names=[movie["name"], *names]),
            "short_description": self.__get_spoilers(text=short_description, names=[movie["name"], *names]),
            "production": [production.value for production in Production.from_countries(countries=countries)],
            "countries": countries,
            "genres": [Genre.from_kinopoisk(genre["name"]).value for genre in movie["genres"]],
            "directors": self.__filter_persons(movie["persons"], "director"),
            "actors": [actor for actor in self.__filter_persons(movie["persons"], "actor") if actor["description"]],
            "duration": movie["movieLength"],
            "rating": {"rating_kp": rating.get("kp", 0), "rating_imdb": rating.get("imdb", 0), "votes_kp": votes.get("kp", 0)},
            "image_urls": [self.__fix_url(image["url"]) for image in images],
            "poster_url": self.__fix_url(movie["poster"]["previewUrl"]),
            "banner_url": self.__fix_url(backdrop["url"]) if backdrop["url"] is not None else None,
            "facts": [self.__get_spoilers(text=BeautifulSoup(fact["value"], "html.parser").text, names=[movie["name"], *names]) for fact in facts] if facts else [],
            "alternative_names": sorted(names),
            "sequels": []
        }

    def __filter_persons(self, persons: List[dict], profession: str) -> List[dict]:
        filtered = []

        for person in persons:
            if person["enProfession"] != profession or not person["name"]:
                continue

            description = person["description"] if person["description"] else ""
            if description in ["дополнительные голоса", "озвучка"]:
                continue

            filtered.append({
                "kinopoisk_id": person["id"],
                "name": person["name"],
                "photo_url": self.__fix_url(person["photo"]),
                "description": description
            })

        return filtered

    def __get_spoilers(self, text: str, names: List[str]) -> dict:
        text = self.__clear_spaces(text)

        names = sorted({name.lower() for name in names}, key=lambda name: -len(name))
        escaped_names = [re.escape(self.__clear_spaces(name)) for name in names]
        spans = set()

        for match in re.finditer(r"|".join(rf"{name}" if " " in name else rf'"{name}"|«{name}»' for name in escaped_names), text.lower()):
            start, end = match.span()

            if match.group().startswith(('"', "«")):
                start, end = start + 1, end - 1

            if not self.__is_span_included(start, end, spans):
                spans.add((start, end))

        for match in re.finditer(r'«[^»]+?»|"[^"]+?"', text.lower()):
            best_ratio = max(ratio(match.group(), name) for name in names)
            start, end = match.span()

            if best_ratio >= 0.8 and not self.__is_span_included(start + 1, end - 1, spans):
                spans.add((start + 1, end - 1))

        return {"text": text, "spoilers": [{"start": start, "end": end} for start, end in sorted(spans)]}

    def __clear_spaces(self, text: str) -> str:
        return re.sub(r"\s+", " ", text).strip()

    def __is_span_included(self, start: int, end: int, spans: Set[Tuple[int, int]]) -> bool:
        for span_start, span_end in spans:
            if span_start <= start <= span_end:
                return True

            if span_start <= end <= span_end:
                return True

            if start <= span_start and span_end <= end:
                return True

            return False

    def __fix_url(self, url: str) -> str:
        kp2api = {
            "https://avatars.mds.yandex.net/get-ott/": "https://image.openmoviedb.com/kinopoisk-ott-images/",
            "https://avatars.mds.yandex.net/get-kinopoisk-image/": "https://image.openmoviedb.com/kinopoisk-images/",
            "https://st.kp.yandex.net/images": "https://image.openmoviedb.com/kinopoisk-st-images/",
            "https://imagetmdb.com/t/p/": "https://image.openmoviedb.com/tmdb-images/",
        }

        for orig_url, api_url in kp2api.items():
            url = url.replace(api_url, orig_url)

        if url.endswith("/x1000"):
            url = f"{url[:-6]}/orig"

        return url

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

            if response.status_code in [403, 500]:
                self.tokens[token] = False
                self.logger.warning(f"WARNING! {response.status_code} error ({response.text})")
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
