import json
import time
import urllib.error
import urllib.request

from models import User


def get_user(user_id: int, retries: int = 3) -> User:
    url = f"https://jsonplaceholder.typicode.com/users/{user_id}"
    last_err = None
    for _ in range(retries):
        try:
            with urllib.request.urlopen(url, timeout=5) as r:
                data = json.loads(r.read().decode())
            return User(id=data["id"], name=data["name"], email=data["email"], age=None)
        except (urllib.error.URLError, TimeoutError, ValueError) as e:
            last_err = e
            time.sleep(1)
    raise last_err

def get_users(retries: int = 3) -> list[User]:
    url = "https://jsonplaceholder.typicode.com/users"
    last_err = None
    for _ in range(retries):
        try:
            with urllib.request.urlopen(url, timeout=5) as r:
                items = json.loads(r.read().decode())
            return [User(id=d["id"], name=d["name"], email=d["email"], age=None) for d in items]
        except (urllib.error.URLError, TimeoutError, ValueError) as e:
            last_err = e
            time.sleep(1)
    raise last_err

def search_users(name: str) -> list[User]:
    all_users = get_users()
    q = name.lower()
    return [u for u in all_users if q in u.name.lower()]

if __name__ == "__main__":
    print(get_user(1))
    print(f"Total: {len(get_users())}")
    print(search_users("Clementine"))
