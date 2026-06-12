import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken


class EncryptionService:
    def __init__(self, secret_key: str) -> None:
        digest = hashlib.sha256(secret_key.encode()).digest()
        key = base64.urlsafe_b64encode(digest)
        self._fernet = Fernet(key)

    def encrypt(self, value: str) -> str:
        return self._fernet.encrypt(value.encode()).decode()

    def decrypt(self, value: str) -> str:
        try:
            return self._fernet.decrypt(value.encode()).decode()
        except InvalidToken as exc:
            raise ValueError("復号に失敗しました") from exc
