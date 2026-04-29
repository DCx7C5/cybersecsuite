# ModuleBase Architecture

**Status**: 🚀 PENDING (Stage 1 Team A)

## Design

Abstract base class for all plugins/modules:

```python
class ModuleBase(ABC):
    @abstractmethod
    async def initialize(self) -> None:
        """Startup: register routes, connect DB, etc."""
        
    @abstractmethod
    def get_routes(self) -> List[APIRoute]:
        """Return FastAPI routes managed by this module."""
        
    @abstractmethod
    async def shutdown(self) -> None:
        """Cleanup on shutdown."""
```

## Modules Extending This
- Marketplace
- A2A
- Accounts
- Hooks
- Manage

## Testing
- [ ] Unit tests: initialize, shutdown
- [ ] Integration: route registration
- [ ] Circular dependency check

## From Legacy
(To be searched in src/legacy/)

## Cannot Use
(Will document as found)
