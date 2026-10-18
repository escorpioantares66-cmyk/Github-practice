import json
import urllib.request

from models import User


def get_user(user_id: int) -> User:
    url = f"https://jsonplaceholder.typicode.com/users/{user_id}"
    with urllib.request.urlopen(url, timeout=10) as r:
        data = json.loads(r.read().decode())
    return User(
        id=data["id"],
        name=data["name"],
        email=data["email"],
        age=None
    )
if __name__ == "__main__":
    u = get_user(1)
    print(u)
