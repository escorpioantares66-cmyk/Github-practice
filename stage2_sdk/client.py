import requests

from .models import User

BASE_URL = "https://jsonplaceholder.typicode.com"

def get_user(user_id: int) -> User:
    url = f"{BASE_URL}/users/{user_id}"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return User(**resp.json())

def get_users() -> list[User]:
    url = f"{BASE_URL}/users"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return [User(**u) for u in resp.json()]

def search_users(name: str) -> list[User]:
    name_lower = name.lower()
    return [u for u in get_users() if name_lower in u.name.lower()]
