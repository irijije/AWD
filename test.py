import hashlib

text = 'aoeu'
enc = hashlib.md5()
enc.update(text.encode())
print(enc.hexdigest())