import re
from dataclasses import dataclass


@dataclass
class User:
    id: int
    name: str
    email: str
    age: int | None = None
    def __post_init__(self):
        if self.id <= 0:
            raise ValueError("id must be > 0")
        if len(self.name) < 2:
            raise ValueError("name must have at least 2 letters")
        if not re.match(r"[^@]+@[^@]+\.[^@]+", self.email):
            raise ValueError("email must have @ like bob@gmail.com")
        if self.age is not None and not (0 <= self.age <= 120):
            raise ValueError("age must be 0-120")
