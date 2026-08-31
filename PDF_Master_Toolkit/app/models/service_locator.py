"""Service Locator pattern for dependency injection."""
from typing import Any, TypeVar, Type

T = TypeVar("T")


class ServiceLocator:
    """Central registry for application services."""

    _instance = None
    _services: dict[str, Any] = {}

    def __new__(cls) -> "ServiceLocator":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._services = {}
        return cls._instance

    def register(self, name: str, service: Any) -> None:
        """Register a service instance."""
        self._services[name] = service

    def get(self, name: str) -> Any:
        """Get a registered service by name."""
        service = self._services.get(name)
        if service is None:
            raise KeyError(f"Service '{name}' not registered.")
        return service

    def get_typed(self, name: str, service_type: Type[T]) -> T:
        """Get a service with type checking."""
        service = self.get(name)
        if not isinstance(service, service_type):
            raise TypeError(
                f"Service '{name}' is not of type {service_type.__name__}"
            )
        return service

    def has(self, name: str) -> bool:
        """Check if a service is registered."""
        return name in self._services

    def unregister(self, name: str) -> None:
        """Remove a service from the registry."""
        self._services.pop(name, None)

    def clear(self) -> None:
        """Clear all registered services."""
        self._services.clear()
