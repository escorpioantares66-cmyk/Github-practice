from client import search_users

print("Test search Clementine")
results = search_users("Clementine")
print(f"GOOD: Found {len(results)}")
for u in results:
    print(u)

print("\nTest search Leanne")
results = search_users("Leanne")
print(f"GOOD: Found {len(results)}")
for u in results:
    print(u)
