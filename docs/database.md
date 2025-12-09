# Database

Pynidus provides decorators for database transaction management, primarily designed for use with SQLAlchemy (or any resource that fits the pattern).

## Transactional Decorator

The `@Transactional()` decorator ensures that a method runs within a database transaction. It commits on success and rolls back on failure.

```python
from pynidus import Injectable, Transactional

@Injectable()
class UserService:
    def __init__(self, repository: UserRepository):
        self.repo = repository

    @Transactional()
    def create_user(self, user_dto):
        user = self.repo.save(user_dto)
        # If this line raises an error, the transaction rolls back
        self.repo.save_profile(user.id, user_dto.profile) 
        return user
```

## Async Support

`@Transactional()` supports `async` methods out of the box.

```python
    @Transactional()
    async def create_user_async(self, user_dto):
        await self.repo.save(user_dto)
```

## Requirements

For the `@Transactional` decorator to work, your service class (or the class using it) typically needs access to a `TransactionManager` or be set up in a way that the decorator can resolve the session/transaction context (implementation details depend on your specific DB setup, often integrated via DI).
