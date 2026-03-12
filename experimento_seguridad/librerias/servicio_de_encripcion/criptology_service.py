import base64
import hashlib
from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

class CryptologyService(object):

    def __init__(self, key): 
        self.bs = AES.block_size
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, raw,key,iv):
        raw = self._pad(raw)
        derived_key = base64.b64decode(key)
        cipher = AES.new(derived_key, AES.MODE_CBC, iv.encode('utf-8'))
        return base64.b64encode(cipher.encrypt(raw.encode()))

    def decrypt(self, enc,key,iv):
        enc = base64.b64decode(enc)
        derived_key = base64.b64decode(key)
        cipher = AES.new(derived_key, AES.MODE_CBC, iv.encode('utf-8'))
        return unpad(cipher.decrypt(enc),16).decode("utf-8")

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]
