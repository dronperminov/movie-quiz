from collections import defaultdict
from typing import Dict, List, Set

from src import database, kinopoisk_parser, movie_database


def dfs(edge_list: Dict[int, set], component: Set[int], visited: Set[int], movie_id: int) -> None:
    component.add(movie_id)
    visited.add(movie_id)

    for v in edge_list[movie_id]:
        if v in visited:
            continue

        dfs(edge_list, component, visited, v)


def get_components(edge_list: Dict[int, Set[int]]) -> List[List[int]]:
    components = []
    visited = set()

    for movie_id in edge_list:
        if movie_id in visited:
            continue

        component = set()
        dfs(edge_list, component, visited, movie_id)
        movie_id2year = {movie.movie_id: movie.year for movie in movie_database.get_movies(movie_ids=list(component))}
        components.append(sorted(component, key=lambda component_id: -movie_id2year[component_id]))

    return components


def main() -> None:
    database.connect()
    page_size = 750

    all_movies = list(database.movies.find({"source.name": "kinopoisk"}))
    edge_list: Dict[int, set] = defaultdict(set)

    for page in range((len(all_movies) + page_size - 1) // page_size):
        movies = all_movies[page * page_size:(page + 1) * page_size]
        kinopoisk_id2movie = {movie["source"]["kinopoisk_id"]: movie for movie in movies}
        sequels = kinopoisk_parser.parse_sequels(movie_ids=list(kinopoisk_id2movie))

        for kinopoisk_id, movie_sequels in sequels.items():
            for sequel_movie in database.movies.find({"source.kinopoisk_id": {"$in": [sequel["id"] for sequel in movie_sequels]}}).sort({"year": -1}):
                edge_list[kinopoisk_id2movie[kinopoisk_id]["movie_id"]].add(sequel_movie["movie_id"])
                edge_list[sequel_movie["movie_id"]].add(kinopoisk_id2movie[kinopoisk_id]["movie_id"])

    for component in get_components(edge_list):
        movie_names = []

        for movie_id in component:
            movie = movie_database.get_movie(movie_id=movie_id)
            movie_names.append(movie.name)
            sequels = [sequel_id for sequel_id in component if movie_id != sequel_id]
            movie_database.update_movie(movie_id=movie_id, diff=movie.get_diff({"sequels": sequels}), username="dronperminov")

        print("\n".join(movie_names))
        print("---------------------------------------")


if __name__ == "__main__":
    main()
