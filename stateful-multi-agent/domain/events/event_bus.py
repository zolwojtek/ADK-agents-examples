"""
Event Bus for domain event publishing and handling.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Set
from datetime import datetime
import threading
from queue import Queue, Empty
import logging

from .domain_event import DomainEvent


class EventHandler(ABC):
    """Abstract base class for event handlers."""
    
    @abstractmethod
    def handle(self, event: DomainEvent) -> None:
        """Handle a domain event."""
        pass
    
    @property
    @abstractmethod
    def handler_name(self) -> str:
        """Get the name of this handler for logging."""
        pass


class EventBus:
    """Simple in-memory event bus for domain events."""
    
    def __init__(self):
        self._handlers: Dict[str, List[EventHandler]] = {}
        self._event_queue = Queue()
        self._processing = False
        self._thread = None
        self._lock = threading.Lock()
        self._logger = logging.getLogger(__name__)
    
    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        """Subscribe a handler to an event type."""
        with self._lock:
            if event_type not in self._handlers:
                self._handlers[event_type] = []
            self._handlers[event_type].append(handler)
            self._logger.info(f"Handler {handler.handler_name} subscribed to {event_type}")
    
    def unsubscribe(self, event_type: str, handler: EventHandler) -> None:
        """Unsubscribe a handler from an event type."""
        with self._lock:
            if event_type in self._handlers:
                try:
                    self._handlers[event_type].remove(handler)
                    self._logger.info(f"Handler {handler.handler_name} unsubscribed from {event_type}")
                except ValueError:
                    self._logger.warning(f"Handler {handler.handler_name} was not subscribed to {event_type}")
    
    def publish(self, event: DomainEvent) -> None:
        """Publish an event to the bus."""
        event_type = getattr(event, "__event_type__", type(event).__name__)
        self._logger.info(f"Publishing event {event_type} with ID {event.event_id}")
        
        self._event_queue.put(event)
        self._start_processing()
    
    def publish_sync(self, event: DomainEvent) -> None:
        """Publish an event synchronously (for testing)."""
        event_type = getattr(event, "__event_type__", type(event).__name__)
        self._logger.info(f"Publishing event {event_type} synchronously")
        
        self._handle_event(event)
    
    def _start_processing(self) -> None:
        """Start processing events in background thread."""
        with self._lock:
            if not self._processing:
                self._processing = True
                self._thread = threading.Thread(target=self._process_events, daemon=True)
                self._thread.start()
                self._logger.info("Started event processing thread")
    
    def _process_events(self) -> None:
        """Process events from the queue."""
        while True:
            try:
                event = self._event_queue.get(timeout=1)
                self._handle_event(event)
                self._event_queue.task_done()
            except Empty:
                with self._lock:
                    if self._event_queue.empty():
                        self._processing = False
                        self._logger.info("Event processing thread stopped")
                        break
    
    def _handle_event(self, event: DomainEvent) -> None:
        """Handle a single event."""
        event_type = getattr(event, "__event_type__", type(event).__name__)
        handlers = self._handlers.get(event_type, [])
        
        self._logger.info(f"Handling event {event_type} with {len(handlers)} handlers")
        
        for handler in handlers:
            try:
                handler.handle(event)
                self._logger.info(f"Handler {handler.handler_name} processed event {event_type}")
            except Exception as e:
                self._logger.error(f"Error in handler {handler.handler_name} for event {event_type}: {e}")
    
    def get_subscribed_handlers(self, event_type: str) -> List[EventHandler]:
        """Get all handlers subscribed to an event type."""
        return self._handlers.get(event_type, []).copy()
    
    def get_all_subscriptions(self) -> Dict[str, List[str]]:
        """Get all subscriptions for debugging."""
        return {
            event_type: [handler.handler_name for handler in handlers]
            for event_type, handlers in self._handlers.items()
        }
    
    def clear_subscriptions(self) -> None:
        """Clear all subscriptions (for testing)."""
        with self._lock:
            self._handlers.clear()
            self._logger.info("All subscriptions cleared")
