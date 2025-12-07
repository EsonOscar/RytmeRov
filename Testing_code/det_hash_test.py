import hashlib
import hmac
import os

pepper = os.environ.get("CPR_PEPPER")

data1 = "12345"
data2 = "asd"
data3 = "qwerty"


# Create deterministic hashes, so we can use search for them in the DB, generate_password_hash() = bad >:|
hash_test1 = hmac.new(pepper.encode(), data1.encode(), hashlib.sha256).hexdigest()
hash_test2 = hmac.new(pepper.encode(), data2.encode(), hashlib.sha256).hexdigest()
hash_test3 = hmac.new(pepper.encode(), data3.encode(), hashlib.sha256).hexdigest()

print(hash_test1)
print(hash_test2)
print(hash_test3)
