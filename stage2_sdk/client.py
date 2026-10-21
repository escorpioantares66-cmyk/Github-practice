import logging

import requests

logger = logging.getLogger(__name__)

BASE_URL = "https://jsonplaceholder.typicode.com"

class APIError(Exception):
    pass

def _request(path: str):
    try:
        url = f"{BASE_URL}{path}"
        logger.debug(f"GET {url}")
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        logger.error(f"Request failed: {e}")
        raise APIError(str(e)) from e

def get_user(user_id: int):
    from .models import User
    data = _request(f"/users/{user_id}")
    return User(**data)

def get_users():
    from .models import User
    data = _request("/users")
    return [User(**u) for u in data]

def search_users(name: str):
    return [u for u in get_users() if name.lower() in u.name.lower()]
