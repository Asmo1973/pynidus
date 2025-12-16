import os

# Set env vars BEFORE importing BaseSettings to ensure they are picked up if loaded on import
# Although pydantic BaseSettings reads os.environ at instantiation time usually.
os.environ["DATABASE__URL"] = "postgres://user:pass@localhost:5432/mydb"
os.environ["TRANSPORT_ZEROMQ__HOST"] = "10.0.0.1"
os.environ["TRANSPORT_RABBITMQ__EXCHANGE_NAME"] = "my_exchange"

from pynidus.core.config import BaseSettings

def verify():
    print("Instantiating BaseSettings...")
    settings = BaseSettings()

    print(f"DB URL: {settings.database.url}")
    print(f"ZMQ Host: {settings.transport_zeromq.host}")
    print(f"RABBIT Exchange: {settings.transport_rabbitmq.exchange_name}")

    assert settings.database.url == "postgres://user:pass@localhost:5432/mydb", f"Expected 'postgres://user:pass@localhost:5432/mydb', got '{settings.database.url}'"
    assert settings.transport_zeromq.host == "10.0.0.1", f"Expected '10.0.0.1', got '{settings.transport_zeromq.host}'"
    assert settings.transport_rabbitmq.exchange_name == "my_exchange", f"Expected 'my_exchange', got '{settings.transport_rabbitmq.exchange_name}'"
    print("Verification successful!")

if __name__ == "__main__":
    verify()
