from typing import Protocol, Any, Callable, TypeVar, Optional, Union
from functools import wraps
import inspect

T = TypeVar("T")

class TransactionManager(Protocol):
    def begin(self) -> Any:
        ...

    def commit(self) -> Any:
        ...

    def rollback(self) -> Any:
        ...

class AsyncTransactionManager(Protocol):
    async def begin(self) -> Any:
        ...

    async def commit(self) -> Any:
        ...

    async def rollback(self) -> Any:
        ...

def Transactional():
    """
    Decorator that manages a transaction around a method call.
    It expects the instance (self) to have a 'transaction_manager' attribute
    that adheres to the TransactionManager or AsyncTransactionManager protocol.
    """
    def wrapper(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def sync_wrapper(self, *args, **kwargs):
            if not hasattr(self, "transaction_manager"):
                raise AttributeError(f"Instance of {self.__class__.__name__} has no 'transaction_manager' attribute.")
            
            manager: Union[TransactionManager, AsyncTransactionManager] = getattr(self, "transaction_manager")
            
            try:
                manager.begin()
                result = func(self, *args, **kwargs)
                manager.commit()
                return result
            except Exception as e:
                manager.rollback()
                raise e

        @wraps(func)
        async def async_wrapper(self, *args, **kwargs):
            if not hasattr(self, "transaction_manager"):
                raise AttributeError(f"Instance of {self.__class__.__name__} has no 'transaction_manager' attribute.")
            
            manager: Union[TransactionManager, AsyncTransactionManager] = getattr(self, "transaction_manager")
            
            try:
                if inspect.iscoroutinefunction(manager.begin):
                    await manager.begin()
                else:
                    manager.begin()
                
                result = await func(self, *args, **kwargs)
                
                if inspect.iscoroutinefunction(manager.commit):
                    await manager.commit()
                else:
                    manager.commit()
                
                return result
            except Exception as e:
                if inspect.iscoroutinefunction(manager.rollback):
                    await manager.rollback()
                else:
                    manager.rollback()
                raise e

        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
            
    return wrapper
