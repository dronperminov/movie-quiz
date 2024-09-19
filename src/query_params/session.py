from dataclasses import dataclass


@dataclass
class SessionCreate:
    session_id: str


@dataclass
class SessionConnect:
    session_id: str
    remove_statistics: bool
