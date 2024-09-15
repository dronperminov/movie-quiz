from dataclasses import dataclass

from src.entities.metadata import Metadata


@dataclass
class Person:
    person_id: int
    kinopoisk_id: int
    name: str
    photo_url: str
    metadata: Metadata

    def to_dict(self) -> dict:
        return {
            "person_id": self.person_id,
            "kinopoisk_id": self.kinopoisk_id,
            "name": self.name,
            "photo_url": self.photo_url,
            "metadata": self.metadata.to_dict()
        }

    @classmethod
    def from_dict(cls: "Person", data: dict) -> "Person":
        return cls(
            person_id=data["person_id"],
            kinopoisk_id=data["kinopoisk_id"],
            name=data["name"],
            photo_url=data["photo_url"],
            metadata=Metadata.from_dict(data["metadata"])
        )

    def get_diff(self, data: dict) -> dict:
        person_data = self.to_dict()
        diff = {}

        fields = ["name", "photo_url"]

        for field in fields:
            if field in data and person_data[field] != data[field]:
                diff[field] = {"prev": person_data[field], "new": data[field]}

        return diff
