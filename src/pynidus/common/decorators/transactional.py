from typing import Protocol, Any, Callable, TypeVar, Optional
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

def Transactional():
    """
    Decorator that manages a transaction around a method call.
    It expects the instance (self) to have a 'transaction_manager' attribute
    that adheres to the TransactionManager protocol.
    """
    def wrapper(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def sync_wrapper(self, *args, **kwargs):
            if not hasattr(self, "transaction_manager"):
                raise AttributeError(f"Instance of {self.__class__.__name__} has no 'transaction_manager' attribute.")
            
            manager: TransactionManager = getattr(self, "transaction_manager")
            
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
            
            manager: TransactionManager = getattr(self, "transaction_manager")
            
            try:
                # Support async managers if needed, but protocol is sync for now.
                # If manager methods are async, we'd need to await them.
                # For simplicity, assuming sync manager methods (common in SQLAlchemy session usage)
                # or we could inspect the manager methods.
                
                # Let's assume sync begin/commit/rollback for now as per plan.
                manager.begin()
                result = await func(self, *args, **kwargs)
                manager.commit()
                return result
            except Exception as e:
                manager.rollback()
                raise e

        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
            
    return wrapper
