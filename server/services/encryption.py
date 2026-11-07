"""Encryption utilities for API keys."""

from cryptography.fernet import Fernet
from server.config import settings


class EncryptionService:
    """Service for encrypting and decrypting API keys."""
    
    def __init__(self):
        self._fernet = None
    
    def _get_fernet(self):
        if self._fernet is None:
            if not settings.encryption_key:
                raise ValueError("Encryption key not configured. Set ENCRYPTION_KEY environment variable.")
            self._fernet = Fernet(settings.encryption_key.encode())
        return self._fernet
    
    def encrypt(self, plaintext: str) -> str:
        """Encrypt a plaintext string."""
        fernet = self._get_fernet()
        return fernet.encrypt(plaintext.encode()).decode()
    
    def decrypt(self, ciphertext: str) -> str:
        """Decrypt a ciphertext string."""
        fernet = self._get_fernet()
        return fernet.decrypt(ciphertext.encode()).decode()


encryption_service = EncryptionService()
