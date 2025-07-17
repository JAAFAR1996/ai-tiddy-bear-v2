from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Dict, Any

T = TypeVar("T")

class HomomorphicEncryptionService(ABC, Generic[T]):
    @abstractmethod
    async def encrypt(self, plaintext: T) -> Any:
        """Encrypts data using homomorphic encryption."""
        pass
        
    @abstractmethod
    async def decrypt(self, ciphertext: Any) -> T:
        """Decrypts homomorphically encrypted data."""
        pass
        
    @abstractmethod
    async def add(self, ciphertext1: Any, ciphertext2: Any) -> Any:
        """Performs addition on two ciphertexts without decryption."""
        pass
        
    @abstractmethod
    async def multiply(self, ciphertext1: Any, ciphertext2: Any) -> Any:
        """Performs multiplication on two ciphertexts without decryption."""
        pass

class ZeroKnowledgeProofService(ABC):
    @abstractmethod
    async def generate_proof(self, statement: Dict[str, Any], private_inputs: Dict[str, Any]) -> Any:
        """Generates a zero-knowledge proof for a given statement and private inputs."""
        pass
        
    @abstractmethod
    async def verify_proof(self, statement: Dict[str, Any], proof: Any) -> bool:
        """Verifies a zero-knowledge proof against a statement."""
        pass