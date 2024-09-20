from src import database, movie_database


def main() -> None:
    database.connect()
    movie_database.download_person_images(output_path="../web/images", username="dronperminov")
    movie_database.download_movie_images(output_path="../web/images", username="dronperminov")
    movie_database.download_tracks_image(output_path="../web/images/tracks", username="dronperminov")
    movie_database.download_tracks(output_path="../web/tracks", username="dronperminov")


if __name__ == "__main__":
    main()
