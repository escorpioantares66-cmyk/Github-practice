from models import User

print("Test 1: Good")
try:
    u = User(id=1, name="Brian", email="brian@gmail.com", age=25)
    print("GOOD:", u)
except ValueError as e:
    print(e)
print("\nTest 2: Bad email should FAIL")
try:
    User(id=2, name="Jo", email="not-email", age=25)
    print("Should not see this")
except ValueError as e:
    print("Correctly rejected:", e)
print("\nTest 3: Short name should FAIL")
try:
    User(id=3, name="A", email="a@gmail.com")
    print("Should not see this")
except ValueError as e:
    print("Correctly rejected:", e)
