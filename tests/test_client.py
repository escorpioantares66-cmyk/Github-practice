from stage2_sdk import get_user, get_users, search_users


def test_get_user():
    u = get_user(1)
    assert u.id == 1
    assert u.name == "Leanne Graham"

def test_get_users():
    users = get_users()
    assert len(users) == 10

def test_search():
    r = search_users("Leanne")
    assert len(r) >= 1
