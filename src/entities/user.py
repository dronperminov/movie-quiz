from dataclasses import dataclass

from src.enums import UserRole


@dataclass
class User:
    username: str
    password_hash: str
    full_name: str
    role: UserRole
    avatar_url: str

    def to_dict(self) -> dict:
        return {
            "username": self.username,
            "password_hash": self.password_hash,
            "full_name": self.full_name,
            "role": self.role.value,
            "avatar_url": self.avatar_url
        }

    @classmethod
    def from_dict(cls: "User", data: dict) -> "User":
        return cls(
            username=data["username"],
            password_hash=data["password_hash"],
            full_name=data["full_name"],
            role=UserRole(data["role"]),
            avatar_url=data["avatar_url"]
        )

    @classmethod
    def from_quiz_dict(cls: "User", data: dict, role: UserRole) -> "User":
        return cls(
            username=data["username"],
            password_hash=data["password_hash"],
            full_name=data["fullname"],
            role=role,
            avatar_url=data["image_src"]
        )

    def to_session(self) -> dict:
        return {
            "username": self.username,
            "full_name": self.full_name,
            "avatar_url": self.avatar_url
        }
