# Microservices

Pynidus supports building microservices with event-driven architectures using RabbitMQ and ZeroMQ.

## Event Listeners

You can define event listeners using the `@OnEvent` decorator.

```python
from pynidus import Controller, OnEvent
from pynidus.microservices import Payload

@Controller()
class OrderController:
    
    @OnEvent("order.created")
    def handle_order_created(self, payload: Payload):
        print(f"Order created: {payload.data}")
```

## Transports

Pynidus abstracts the underlying transport layer.

### RabbitMQ

Install the extra: `uv add "pynidus[rabbitmq]"`

Configure connection settings in your environment variables.

### ZeroMQ

Install the extra: `uv add "pynidus[zeromq]"`

ZeroMQ is useful for high-performance, brokerless messaging between services.

## TRAM Pattern (Transactional Outbox)

For reliable messaging, Pynidus implements the **Transactional Outbox** pattern (often called TRAM in some contexts). This ensures that database updates and event publishing happen atomically.

1. **Transaction**: Your service saves data to the DB and "publishes" an event.
2. **Outbox**: The event is saved to an `outbox` table in the same transaction.
3. **Relay**: A background process (the Relay) reads the outbox and ensures the event is sent to the message broker (RabbitMQ/ZeroMQ).

This prevents "dual write" problems where a DB commit succeeds but message publishing fails (or vice versa).
