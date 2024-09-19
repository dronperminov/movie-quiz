from datetime import datetime
from unittest import TestCase

from src.entities.actor import Actor
from src.entities.cite import Cite
from src.entities.history_action import AddMovieAction, AddPersonAction, EditMovieAction, EditPersonAction, HistoryAction, RemoveMovieAction, RemovePersonAction
from src.entities.lyrics import Lyrics
from src.entities.lyrics_line import LyricsLine
from src.entities.metadata import Metadata
from src.entities.movie import Movie
from src.entities.person import Person
from src.entities.rating import Rating
from src.entities.source import HandSource, KinopoiskSource, Source, YandexSource
from src.entities.spoiler_text import SpoilerText
from src.entities.track import Track
from src.enums import Genre, MovieType, Production


class TestSerialization(TestCase):
    def test_source_serialization(self) -> None:
        sources = [KinopoiskSource(kinopoisk_id=123), YandexSource(yandex_id="14"), HandSource()]

        for source in sources:
            source_dict = source.to_dict()
            source_from_dict = Source.from_dict(source_dict)
            self.assertEqual(source, source_from_dict)

    def test_metadata_serialization(self) -> None:
        metadata = Metadata(
            created_by="user",
            created_at=datetime(2024, 1, 3, 5, 23, 59),
            updated_by="user2",
            updated_at=datetime(2024, 10, 3, 5, 23, 59)
        )

        metadata_dict = metadata.to_dict()
        metadata_from_dict = Metadata.from_dict(metadata_dict)
        self.assertEqual(metadata, metadata_from_dict)

    def test_lyrics_serialization(self) -> None:
        lyrics = Lyrics(
            lines=[LyricsLine(time=0.5, text="line 1"), LyricsLine(time=43.13, text="line 2"), LyricsLine(time=80.8, text="line 3")],
            lrc=True
        )

        lyrics_dict = lyrics.to_dict()
        lyrics_from_dict = Lyrics.from_dict(lyrics_dict)
        self.assertEqual(lyrics, lyrics_from_dict)

    def test_spoiler_text_serialization(self) -> None:
        spoiler_text = SpoilerText(
            text="Some text with spoiler 1 and spoiler 2",
            spoilers=[(15, 24), (29, 38)]
        )

        spoiler_text_dict = spoiler_text.to_dict()
        spoiler_text_from_dict = SpoilerText.from_dict(spoiler_text_dict)
        self.assertEqual(spoiler_text, spoiler_text_from_dict)

    def test_rating_serialization(self) -> None:
        rating = Rating(rating_kp=8.78, rating_imdb=85.24, votes_kp=300234)

        rating_dict = rating.to_dict()
        rating_from_dict = Rating.from_dict(rating_dict)
        self.assertEqual(rating, rating_from_dict)

    def test_cite_serialization(self) -> None:
        cite = Cite(
            cite_id=1,
            movie_id=67,
            text=SpoilerText(text="No spoiler text", spoilers=[]),
            metadata=Metadata.initial(username="user")
        )

        cite_dict = cite.to_dict()
        cite_from_dict = Cite.from_dict(cite_dict)
        self.assertEqual(cite, cite_from_dict)

    def test_track_serialization(self) -> None:
        track = Track(
            track_id=1,
            movie_id=67,
            source=YandexSource(yandex_id="5678"),
            title="Track title",
            artists=["Artist 1", "Artist 2"],
            lyrics=Lyrics(lines=[LyricsLine(time=0.8, text="Line 1")], lrc=True),
            duration=182.6,
            downloaded=False,
            image_url="image_url",
            metadata=Metadata.initial(username="user")
        )

        track_dict = track.to_dict()
        track_from_dict = Track.from_dict(track_dict)
        self.assertEqual(track, track_from_dict)

    def test_person_serialization(self) -> None:
        person = Person(
            person_id=1,
            kinopoisk_id=456,
            name="Person Name",
            photo_url="photo url",
            metadata=Metadata.initial(username="user")
        )

        person_dict = person.to_dict()
        person_from_dict = Person.from_dict(person_dict)
        self.assertEqual(person, person_from_dict)

    def test_actor_serialization(self) -> None:
        actor = Actor(
            person_id=1,
            description="some description"
        )

        actor_dict = actor.to_dict()
        actor_from_dict = Actor.from_dict(actor_dict)
        self.assertEqual(actor, actor_from_dict)

    def test_movie_serialization(self) -> None:
        movie = Movie(
            movie_id=1,
            name="Movie name",
            source=KinopoiskSource(kinopoisk_id=45),
            movie_type=MovieType.MOVIE,
            year=2024,
            slogan="Some slogan text",
            description=SpoilerText(text="Some long description", spoilers=[(5, 9)]),
            short_description=SpoilerText(text="Short text", spoilers=[]),
            production=[Production.RUSSIAN, Production.FOREIGN],
            countries=["Russia", "USA"],
            genres=[Genre.BIOGRAPHY, Genre.HISTORY],
            actors=[Actor(person_id=1, description="description 1"), Actor(person_id=2, description="description 2")],
            directors=[Actor(person_id=5, description="description 3")],
            duration=148.5,
            rating=Rating(rating_kp=1.9, rating_imdb=0.2, votes_kp=678),
            image_urls=["url1", "url2"],
            poster_url="poster_url",
            banner_url="banner_url",
            facts=[SpoilerText(text="fact 1", spoilers=[]), SpoilerText(text="fact 2", spoilers=[])],
            cites=[4, 8, 123],
            tracks=[6, 9, 2345],
            alternative_names=["name1", "another MEGA NAME"],
            metadata=Metadata.initial(username="user"),
            sequels=[2, 6, 8]
        )

        movie_dict = movie.to_dict()
        movie_from_dict = Movie.from_dict(movie_dict)
        self.assertEqual(movie, movie_from_dict)

    def test_history_action_serialization(self) -> None:
        history_actions = [
            AddMovieAction(username="user", timestamp=datetime(2024, 1, 1, 20, 23, 51), movie_id=1),
            EditMovieAction(username="user2", timestamp=datetime(2024, 1, 1, 20, 42, 12), movie_id=1, diff={"name": "aba"}),
            RemoveMovieAction(username="user3", timestamp=datetime(2024, 1, 2, 12, 00, 19), movie_id=1),
            AddPersonAction(username="user", timestamp=datetime(2024, 1, 1, 20, 23, 51), person_id=1),
            EditPersonAction(username="user2", timestamp=datetime(2024, 1, 1, 20, 42, 12), person_id=1, diff={"name": "aba"}),
            RemovePersonAction(username="user", timestamp=datetime(2024, 1, 1, 20, 23, 51), person_id=1),
        ]

        for history_action in history_actions:
            history_action_dict = history_action.to_dict()
            history_action_from_dict = HistoryAction.from_dict(history_action_dict)
            self.assertEqual(history_action, history_action_from_dict)
