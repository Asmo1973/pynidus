import pytest
from unittest.mock import Mock
from pynidus import Transactional, TransactionManager

class MockTransactionManager:
    def __init__(self):
        self.begin = Mock()
        self.commit = Mock()
        self.rollback = Mock()

class TransactionalService:
    def __init__(self, manager):
        self.transaction_manager = manager

    @Transactional()
    def success_method(self):
        return "success"

    @Transactional()
    def error_method(self):
        raise ValueError("error")

    @Transactional()
    async def async_success_method(self):
        return "async_success"

    @Transactional()
    async def async_error_method(self):
        raise ValueError("async_error")

class ServiceMissingManager:
    @Transactional()
    def method(self):
        pass

def test_transactional_success():
    manager = MockTransactionManager()
    service = TransactionalService(manager)

    result = service.success_method()

    assert result == "success"
    manager.begin.assert_called_once()
    manager.commit.assert_called_once()
    manager.rollback.assert_not_called()

def test_transactional_error():
    manager = MockTransactionManager()
    service = TransactionalService(manager)

    with pytest.raises(ValueError):
        service.error_method()

    manager.begin.assert_called_once()
    manager.commit.assert_not_called()
    manager.rollback.assert_called_once()

@pytest.mark.asyncio
async def test_transactional_async_success():
    manager = MockTransactionManager()
    service = TransactionalService(manager)

    result = await service.async_success_method()

    assert result == "async_success"
    manager.begin.assert_called_once()
    manager.commit.assert_called_once()
    manager.rollback.assert_not_called()

@pytest.mark.asyncio
async def test_transactional_async_error():
    manager = MockTransactionManager()
    service = TransactionalService(manager)

    with pytest.raises(ValueError):
        await service.async_error_method()

    manager.begin.assert_called_once()
    manager.commit.assert_not_called()
    manager.rollback.assert_called_once()

def test_missing_manager_attribute():
    service = ServiceMissingManager()
    with pytest.raises(AttributeError, match="has no 'transaction_manager' attribute"):
        service.method()
