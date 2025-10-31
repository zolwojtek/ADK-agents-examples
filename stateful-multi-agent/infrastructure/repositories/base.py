"""
Base repository implementation for in-memory storage.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, TypeVar, Generic
from uuid import uuid4

from domain.shared.value_objects import Identifier

T = TypeVar('T')
ID = TypeVar('ID', bound=Identifier)


class BaseRepository(Generic[T, ID], ABC):
    """Base repository interface."""
    
    @abstractmethod
    def get_by_id(self, id: ID) -> Optional[T]:
        """Get entity by ID."""
        pass
    
    @abstractmethod
    def get_all(self) -> List[T]:
        """Get all entities."""
        pass
    
    @abstractmethod
    def save(self, entity: T) -> T:
        """Save entity."""
        pass
    
    @abstractmethod
    def delete(self, id: ID) -> bool:
        """Delete entity by ID."""
        pass
    
    @abstractmethod
    def exists(self, id: ID) -> bool:
        """Check if entity exists."""
        pass


class InMemoryRepository(BaseRepository[T, ID]):
    """In-memory repository implementation."""
    
    def __init__(self):
        self._entities: Dict[str, T] = {}
    
    def get_by_id(self, id: ID) -> Optional[T]:
        """Get entity by ID."""
        return self._entities.get(id.value)
    
    def get_all(self) -> List[T]:
        """Get all entities."""
        return list(self._entities.values())
    
    def save(self, entity: T) -> T:
        """Save entity."""        
        self._entities[entity.id.value] = entity
        return entity
    
    def delete(self, id: ID) -> bool:
        """Delete entity by ID."""
        if id.value in self._entities:
            del self._entities[id.value]
            return True
        return False
    
    def exists(self, id: ID) -> bool:
        """Check if entity exists."""
        return id.value in self._entities
    
    def clear(self) -> None:
        """Clear all entities."""
        self._entities.clear()
    
    def count(self) -> int:
        """Get count of entities."""
        return len(self._entities)
