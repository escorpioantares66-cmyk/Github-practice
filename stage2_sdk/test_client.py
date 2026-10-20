from client import get_user, get_users, search_users

print("=== SDK FINAL TEST ===")
print("\n1. Single:")
print(get_user(1))

print("\n2. All:")
print(f"Got {len(get_users())} users")

print("\n3. Search:")
for u in search_users("Ervin"):
    print(u)

print("\nGOOD: SDK Week2 complete!")
