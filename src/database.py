import re
from typing import Optional

from pymongo import ASCENDING, MongoClient

from src.entities.settings import Settings
from src.entities.user import User
from src.enums import UserRole


class Database:
    client: MongoClient = None
    identifiers = None
    users = None
    roles = None
    settings = None
    questions = None
    movies = None
    tracks = None
    persons = None
    cites = None
    history = None

    def __init__(self, mongo_url: str, database_name: str) -> None:
        self.mongo_url = mongo_url
        self.database_name = database_name

    def connect(self) -> None:
        self.client = MongoClient(self.mongo_url)
        database = self.client[self.database_name]

        self.identifiers = database["identifiers"]

        for name in ["movies", "cites", "tracks", "persons"]:
            if self.identifiers.find_one({"_id": name}) is None:
                self.identifiers.insert_one({"_id": name, "value": 0})

        self.users = self.client["quiz"]["users"]
        self.roles = database["roles"]
        self.roles.create_index([("username", ASCENDING)], unique=True)

        self.settings = database["settings"]
        self.settings.create_index([("username", ASCENDING)], unique=True)

        self.questions = database["questions"]
        self.questions.create_index([("username", ASCENDING)])
        self.questions.create_index([("datetime", ASCENDING)])

        self.movies = database["movies"]
        self.movies.create_index([("movie_id", ASCENDING)], unique=True)
        self.movies.create_index([("name", ASCENDING)])

        self.persons = database["persons"]
        self.persons.create_index([("person_id", ASCENDING)], unique=True)

        self.tracks = database["tracks"]
        self.tracks.create_index([("track_id", ASCENDING)], unique=True)
        self.tracks.create_index([("movie_id", ASCENDING)], unique=True)

        self.cites = database["cites"]
        self.cites.create_index([("cite_id", ASCENDING)], unique=True)
        self.cites.create_index([("movie_id", ASCENDING)], unique=True)

        self.history = database["history"]
        self.history.create_index([("username", ASCENDING)])
        self.history.create_index([("timestamp", ASCENDING)])

    def get_user(self, username: str) -> Optional[User]:
        if not username:
            return None

        user: dict = self.users.find_one({"username": {"$regex": f"^{re.escape(username)}$", "$options": "i"}})
        if not user:
            return None

        role = self.roles.find_one({"username": user["username"]})
        return User.from_quiz_dict(user, UserRole(role["role"]) if role else UserRole.USER)

    def get_identifier(self, collection_name: str) -> int:
        identifier = self.identifiers.find_one_and_update({"_id": collection_name}, {"$inc": {"value": 1}}, return_document=True)
        return identifier["value"]

    def get_settings(self, username: str) -> Settings:
        settings = self.settings.find_one_and_update({"username": username}, {"$setOnInsert": Settings.default(username).to_dict()}, upsert=True, return_document=True)
        return Settings.from_dict(settings)

    def update_settings(self, settings: Settings) -> None:
        self.settings.update_one({"username": settings.username}, {"$set": settings.to_dict()})

    def drop(self) -> None:
        self.client.drop_database(self.database_name)

    def close(self) -> None:
        self.client.close()
