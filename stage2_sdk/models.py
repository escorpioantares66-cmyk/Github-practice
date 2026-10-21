from dataclasses import dataclass, field
from typing import Any


@dataclass
class User:
    id: int
    name: str
    email: str
    username: str = ""
    phone: str = ""
    website: str = ""
    address: dict[str, Any] = field(default_factory=dict)
    company: dict[str, Any] = field(default_factory=dict)

    def __str__(self):
        return f"User(id={self.id}, name='{self.name}', username='{self.username}', email='{self.email}')"

    __repr__ = __str__
