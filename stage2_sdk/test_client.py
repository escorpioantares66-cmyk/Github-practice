from client import get_user

print("Test fetch user 1 from jsonplaceholder")
try:
    u = get_user(1)
    print("GOOD:", u)
except ValueError as e:
    print("FAIL:", e)
print("\nTest fetch user 2")
try:
    u = get_user(2)
    print("GOOD:", u)
except ValueError as e:
    print("FAIL:", e)
