from client import get_user, get_users
print("Test get_user(1)")
print(get_user(1))
print("\nTest get_users()")
users = get_users()
print(f"GOOD: Got {len(users)} users")
for u in users[:3]:
    print(u)
