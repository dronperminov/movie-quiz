from dataclasses import dataclass


@dataclass
class SignIn:
    username: str
    password: str
