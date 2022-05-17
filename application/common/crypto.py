import base64
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import padding as symmetric_padding
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet
import os

class Crypto:
    _PrivateKey = None

    def LoadKeys():
        if not os.path.exists("keys"):
            os.mkdir("keys")
        
        if os.path.exists("keys/private"):
            try:
                with open("keys/private", "rb") as f:
                    Crypto._PrivateKey = Crypto.ImportPrivateKey(f.read())
            except:
                Crypto.SaveKeys()
        else:
            Crypto.SaveKeys()

    def ImportPublicKey(public_key_bytes):
        return serialization.load_pem_public_key(public_key_bytes)

    def ImportPrivateKey(private_key_bytes):
        return serialization.load_pem_private_key(
            private_key_bytes,
            password=None,
        )
    
    def ExportPublicKey():
        return Crypto._PrivateKey.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    def SaveKeys():
        if not Crypto._PrivateKey:
            Crypto.GenerateKeys()

        private_pem = Crypto._PrivateKey.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )

        with open("keys/private", "wb") as f:
            f.write(private_pem)

    def GenerateKeys():
        Crypto._PrivateKey = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )

    def GetPrivateKey():
        if not Crypto._PrivateKey:
            Crypto.GenerateKeys()
        return Crypto._PrivateKey

    def Encrypt(data, key):
        return Fernet(base64.b64encode(key)).encrypt(data)
    
    def Decrypt(data, key):
        return Fernet(base64.b64encode(key)).decrypt(data)

    def RSAEncrypt(data, public_key):
        return public_key.encrypt(
            data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
    
    def RSADecrypt(data):
        return Crypto._PrivateKey.decrypt(
            data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
    