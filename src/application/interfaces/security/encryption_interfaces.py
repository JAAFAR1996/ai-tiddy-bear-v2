from abc import ABC, abstractmethod
from typing import Any, TypeVar

T = TypeVar("T")


class HomomorphicEncryptionService[T](ABC):
    @abstractmethod
    async def encrypt(self, plaintext: T) -> Any:
        """Encrypts data using homomorphic encryption."""

    @abstractmethod
    async def decrypt(self, ciphertext: Any) -> T:
        """Decrypts homomorphically encrypted data."""

    @abstractmethod
    async def add(self, ciphertext1: Any, ciphertext2: Any) -> Any:
        """Performs addition on two ciphertexts without decryption."""

    @abstractmethod
    async def multiply(self, ciphertext1: Any, ciphertext2: Any) -> Any:
        """Performs multiplication on two ciphertexts without decryption."""


class ZeroKnowledgeProofService(ABC):
    @abstractmethod
    async def generate_proof(
        self,
        statement: dict[str, Any],
        private_inputs: dict[str, Any],
    ) -> Any:
        """Generates a zero-knowledge proof for a given statement and private inputs."""

    @abstractmethod
    async def verify_proof(self, statement: dict[str, Any], proof: Any) -> bool:
        """Verifies a zero-knowledge proof against a statement."""
