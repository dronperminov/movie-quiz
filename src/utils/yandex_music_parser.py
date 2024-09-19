from typing import Callable, Iterable, List, Optional, Union

from yandex_music import Artist, Client, DownloadInfo, Playlist, Track
from yandex_music.exceptions import BadRequestError, NetworkError, NotFoundError, TimedOutError, UnauthorizedError

from src.entities.lyrics import Lyrics


class YandexMusicParser:
    def __init__(self, token: str, covers_size: str = "400x400") -> None:
        self.token = token
        self.client = None
        self.covers_size = covers_size

    def parse_tracks(self, track_ids: List[str]) -> List[dict]:
        tracks = self.__request(func=lambda: self.client.tracks(track_ids=track_ids))
        return [self.__process_track(track) for track in tracks]

    def parse_playlist(self, playlist_id: str, playlist_username: str, max_tracks: int = 20) -> Optional[List[dict]]:
        try:
            playlist = self.__request(func=lambda: self.client.users_playlists(playlist_id, playlist_username))
            return [self.__process_track(track.track) for track in playlist.tracks[:max_tracks]]
        except NotFoundError:
            return None

    def get_track_link(self, track_id: str, bitrate: int = 192) -> Optional[str]:
        try:
            info = self.__request(func=lambda: self.client.tracks([track_id])[0].get_specific_download_info("mp3", bitrate))
            return info.get_direct_link()
        except (BadRequestError, UnauthorizedError):
            return None

    def get_download_info(self, track_ids: List[str], bitrate: int = 192) -> Iterable[Optional[DownloadInfo]]:
        for track in self.__request(func=lambda: self.client.tracks(track_ids)):
            try:
                yield self.__request(func=lambda: track.get_specific_download_info("mp3", bitrate))  # noqa
            except UnauthorizedError:
                yield None

    def __process_track(self, track: Track) -> dict:
        lyrics = self.__get_lyrics(track)

        return {
            "yandex_id": str(track.id),
            "title": track.title,
            "artists": self.__get_artists(track),
            "lyrics": lyrics.to_dict() if lyrics else None,
            "duration": round(track.duration_ms / 1000, 2) if track.duration_ms else 0,
            "image_url": track.get_cover_url(self.covers_size) if track.cover_uri else None
        }

    def __get_artists(self, track: Track) -> List[str]:
        artists = []

        for artist in track.artists:
            artists.append(artist.name)

            if not artist.decomposed:
                continue

            for decomposed_artist in artist.decomposed:
                if isinstance(decomposed_artist, Artist):
                    artists.append(decomposed_artist.name)

        return artists

    def __get_lyrics(self, track: Track) -> Optional[Lyrics]:
        if track.lyrics_info is not None:
            if track.lyrics_info.has_available_sync_lyrics:
                return Lyrics.from_lrc(self.__request(func=lambda: track.get_lyrics("LRC").fetch_lyrics()))

            if track.lyrics_info.has_available_text_lyrics:
                return Lyrics.from_text(self.__request(func=lambda: track.get_lyrics("TEXT").fetch_lyrics()))

            return None

        try:
            return Lyrics.from_lrc(track.get_lyrics("LRC").fetch_lyrics())
        except NotFoundError:
            pass

        try:
            return Lyrics.from_text(track.get_lyrics("TEXT").fetch_lyrics())
        except NotFoundError:
            pass

        return None

    def __request(self, func: Callable, max_retries: int = 5) -> Union[dict, list, str, Playlist]:
        if self.client is None:
            self.client = Client(self.token).init()

        for _ in range(max_retries):
            try:
                return func()
            except (BadRequestError, TimedOutError):
                continue
            except NetworkError as error:
                if str(error) == "Bad Gateway":
                    continue

                raise error

        raise ValueError("Unable to make request")
