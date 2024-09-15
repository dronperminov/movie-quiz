from dataclasses import dataclass, field


@dataclass
class Source:
    name: str = field(init=False)

    def to_dict(self) -> dict:
        return {"name": self.name}

    @classmethod
    def from_dict(cls: "Source", data: dict) -> "Source":
        if data["name"] == KinopoiskSource.name:
            return KinopoiskSource(kinopoisk_id=data["kinopoisk_id"])

        if data["name"] == YandexSource.name:
            return YandexSource(yandex_id=data["yandex_id"])

        if data["name"] == HandSource.name:
            return HandSource()

        raise ValueError(f'Invalid source name "{data["name"]}"')


@dataclass
class KinopoiskSource(Source):
    kinopoisk_id: int
    name = "kinopoisk"

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            "kinopoisk_id": self.kinopoisk_id
        }


@dataclass
class YandexSource(Source):
    yandex_id: str
    name = "yandex"

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            "yandex_id": self.yandex_id
        }


@dataclass
class HandSource(Source):
    name = "hand"

    def to_dict(self) -> dict:
        return super().to_dict()
