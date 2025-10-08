"""Singleton pattern for Repository management."""
from typing import Optional
from coderag import Repository


class RepositorySingleton:
    """Singleton class to manage a single Repository instance."""
    
    _instance: Optional['RepositorySingleton'] = None
    _repository: Optional[Repository] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def initialize(self, repository: Repository) -> None:
        """Initialize the singleton with a Repository instance.
        
        Args:
            repository: The Repository instance to use
        """
        self._repository = repository
    
    def get_repository(self) -> Repository:
        """Get the Repository instance.
        
        Returns:
            Repository: The singleton Repository instance
            
        Raises:
            RuntimeError: If repository has not been initialized
        """
        if self._repository is None:
            raise RuntimeError(
                "Repository not initialized. Call initialize() first."
            )
        return self._repository
    
    @classmethod
    def reset(cls) -> None:
        """Reset the singleton instance (useful for testing)."""
        cls._instance = None
        if cls._instance:
            cls._instance._repository = None


# Global accessor function for convenience
def get_repository() -> Repository:
    """Get the singleton Repository instance.
    
    Returns:
        Repository: The singleton Repository instance
        
    Raises:
        RuntimeError: If repository has not been initialized
    """
    return RepositorySingleton().get_repository()
