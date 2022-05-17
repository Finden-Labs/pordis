from common.crypto import Crypto

import os

class User:
    def __init__(self, username=b""):
        self.username = username
        self.unique_id = b""
        self.is_admin = False
        self.public_key = None
        self.address = ""
        self.socket = None
        self.shared_secret = ""
        self.encryption_enabled = False
    
    def set_public_key(self, public_key_bytes):
        self.public_key = Crypto.ImportPublicKey(public_key_bytes)
    
    def disconnect(self):
        if self.socket:
            self.socket.close()
            self.socket = None