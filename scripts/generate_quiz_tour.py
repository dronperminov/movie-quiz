import os
import random
from argparse import ArgumentParser, Namespace
from typing import List

from src import database, questions_database, quiz_tours_database
from src.entities.question_settings import QuestionSettings
from src.enums import MovieType, Production, QuestionType
from src.enums import QuizTourType


def get_random_picture(dir_name: str) -> str:
    image_name = random.choice(os.listdir(os.path.join("..", "web", "images", "quiz_tours", dir_name)))
    return f"/images/quiz_tours/{dir_name}/{image_name}"


def get_tags(args: Namespace) -> List[str]:
    tags = []

    if args.votes >= 200_000:
        tags.append("top")

    if args.years == "soviet" and args.production == "russian":
        tags.append("soviet")

    if args.movie_types in ["movie", "series", "cartoon", "anime", "mcs"]:
        tags.append(args.movie_types)

    return tags


def main() -> None:
    parser = ArgumentParser(description="Script for QuizTour generation")
    parser.add_argument("--name", help="Name of the quiz tour", type=str, required=True)
    parser.add_argument("--description", help="Description of the quiz tour", type=str, required=True)
    parser.add_argument("--questions", help="Number of questions", type=int, required=True)
    parser.add_argument("--image", help="Path to dir with image", type=str, required=True)
    parser.add_argument("--years", help="", choices=("all", "normal", "soviet"), default="normal")
    parser.add_argument("--movie-types", help="", choices=("all", "mcs", "movie", "series", "cartoon", "anime"), default="mcs")
    parser.add_argument("--production", help="", choices=("all", "russian", "foreign"), default="all")
    parser.add_argument("--mechanics", help="", choices=("regular", "alphabet", "stairs", "letter", "n_letters", "miracles_field", "chain"), default="regular")
    parser.add_argument("--votes", help="Min border of kinopoisk votes count", type=int, default=10_000)
    parser.add_argument("--question-types", help="", choices=("all", "images", "images-short-description"), default="all")

    args = parser.parse_args()
    assert args.questions >= 7

    database.connect()

    years = {
        "all": {(1980, 1989): 1, (1990, 1999): 1, (2000, 2009): 1, (2010, 2014): 1, (2015, 2019): 1, (2020, ""): 1},
        "normal": {(1980, 1989): 0.25, (1990, 1999): 0.5, (2000, 2009): 1, (2010, 2014): 2, (2015, 2019): 2, (2020, ""): 3},
        "soviet": {("", 1979): 1, (1980, 1989): 1}
    }[args.years]

    movie_types = {
        "all": {MovieType.MOVIE: 1, MovieType.SERIES: 1, MovieType.CARTOON: 1, MovieType.ANIMATED_SERIES: 1, MovieType.ANIME: 1},
        "mcs": {MovieType.MOVIE: 4, MovieType.SERIES: 1.5, MovieType.CARTOON: 1, MovieType.ANIMATED_SERIES: 0.5},
        "movie": {MovieType.MOVIE: 1},
        "series": {MovieType.SERIES: 1},
        "cartoon": {MovieType.CARTOON: 0.9, MovieType.ANIMATED_SERIES: 0.1},
        "anime": {MovieType.ANIME}
    }[args.movie_types]

    production = {
        "all": {Production.FOREIGN: 0.8, Production.RUSSIAN: 0.1, Production.TURKISH: 0.05, Production.KOREAN: 0.05},
        "russian": {Production.RUSSIAN: 1},
        "foreign": {Production.FOREIGN: 1}
    }[args.production]

    mechanics = {
        "regular": QuizTourType.REGULAR,
        "alphabet": QuizTourType.ALPHABET,
        "stairs": QuizTourType.STAIRS,
        "letter": QuizTourType.LETTER,
        "n_letters": QuizTourType.N_LETTERS,
        "miracles_field": QuizTourType.MIRACLES_FIELD,
        "chain": QuizTourType.CHAIN
    }[args.mechanics]

    question_types = {
        "all": {QuestionType.MOVIE_BY_IMAGE: 2, QuestionType.MOVIE_BY_SHORT_DESCRIPTION: 1, QuestionType.MOVIE_BY_ACTORS: 0.1, QuestionType.MOVIE_BY_CHARACTERS: 0.2},
        "images": {QuestionType.MOVIE_BY_IMAGE: 1},
        "images-short-description": {QuestionType.MOVIE_BY_IMAGE: 2, QuestionType.MOVIE_BY_SHORT_DESCRIPTION: 1}
    }[args.question_types]

    settings = QuestionSettings(
        answer_time=0,
        movie_types=movie_types,
        production=production,
        years=years,
        votes=(args.votes, ""),
        question_types=question_types,
        repeat_incorrect_probability=0,
        hide_actor_photos=False
    )

    params = {
        "name": args.name,
        "description": args.description,
        "image_url": get_random_picture(args.image),
        "tags": get_tags(args)
    }

    print("Generation parameters:")
    print(f'- name: {params["name"]}')
    print(f'- description: {params["description"]}')
    print(f"- questions count: {args.questions}")
    print(f'- image URL: {params["image_url"]}')
    print(f'- tags: {params["tags"]}')
    print(f"- mechanics: {mechanics}\n")

    print("Generation settings:")
    print(f"- years: {settings.years}")
    print(f"- movie types: {settings.movie_types}")
    print(f"- production: {settings.production}")
    print(f"- votes: {settings.votes}")
    print(f"- hide actor photos: {settings.hide_actor_photos}")
    print(f"- question type: {settings.question_types}")

    answer = input("Write yes for continue >")

    if answer != "yes":
        return

    questions_database.alpha = 0.999999
    questions_database.last_questions_count = 10000
    quiz_tours_database.generate_tour(params, quiz_tour_type=mechanics, settings=settings, questions_count=args.questions)


if __name__ == "__main__":
    main()
