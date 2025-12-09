import pytest
from unittest.mock import patch, MagicMock
from pynidus import NidusFactory, Module, Controller, Get
from pynidus.core.config import BaseSettings
import os

def test_nidus_listen_default_config():
    @Module()
    class TestModule:
        pass
    
    with patch("uvicorn.run") as mock_run:
        NidusFactory.listen(TestModule)
        
        args, kwargs = mock_run.call_args
        assert kwargs["host"] == "0.0.0.0"
        assert kwargs["port"] == 3000
        assert kwargs["ssl_keyfile"] is None
        assert kwargs["ssl_certfile"] is None

def test_nidus_listen_env_config():
    @Module()
    class TestModule:
        pass
    
    # Mock environment variables
    with patch.dict(os.environ, {
        "SERVER__HOST": "127.0.0.1",
        "SERVER__PORT": "8080",
        "SERVER__SSL_KEYFILE": "/path/to/key",
        "SERVER__SSL_CERTFILE": "/path/to/cert"
    }):
        with patch("uvicorn.run") as mock_run:
            NidusFactory.listen(TestModule)
            
            args, kwargs = mock_run.call_args
            assert kwargs["host"] == "127.0.0.1"
            assert kwargs["port"] == 8080
            assert kwargs["ssl_keyfile"] == "/path/to/key"
            assert kwargs["ssl_certfile"] == "/path/to/cert"

def test_nidus_listen_override():
    @Module()
    class TestModule:
        pass
        
    with patch("uvicorn.run") as mock_run:
        # Kwargs should override env/default
        NidusFactory.listen(TestModule, port=9090)
        
        args, kwargs = mock_run.call_args
        assert kwargs["port"] == 9090
