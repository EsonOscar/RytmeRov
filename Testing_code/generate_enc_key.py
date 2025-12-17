from cryptography.fernet import Fernet
import hashlib
import os

print(Fernet.generate_key())
"""


file_name = Fernet.generate_key()#.decode()[:-1]
print(file_name)

data = b'asdf'

print(data)

f = Fernet(file_name)

token = f.encrypt(data)
print(token)

print(f.decrypt(token))
"""

key = os.getenv("ENC_KEY").encode()

data = "ASDS"
data2 = "ADSS"
data3 = "ASDS"
"""
with open("/home/3semprojekt/RytmeRov/flask/ecg/2Vn6PvTdy1y_cRXJCflC5CSDqGz7VZ_FbPgtzJNModE.csv", "r") as f:
    data = f.read()
    
print(data)
"""
fer = Fernet(key)

data = fer.encrypt(data.encode())
data2 = fer.encrypt(data2.encode())
data3 = fer.encrypt(data3.encode())
"""
with open("/home/3semprojekt/RytmeRov/flask/recv_data.txt", "w") as f:
    f.write(data.decode())
"""
#print(data)
#print(data2)
#print(data3)