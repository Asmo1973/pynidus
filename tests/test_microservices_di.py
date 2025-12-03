import pytest
import asyncio
from pynidus.core.container import Container
from pynidus.common.decorators.controller import Controller
from pynidus.common.decorators.injectable import Injectable
from pynidus.microservices.decorators import EventPattern
from pynidus.microservices.listener import MicroserviceListener
from pynidus.microservices.transport.memory import MemoryTransport

# Reset container for test isolation
@pytest.fixture(autouse=True)
def reset_container():
    Container._instance = None
    yield

@Injectable()
class GreetingService:
    def greet(self, name: str):
        return f"Hello, {name}!"

@Controller()
class UserController:
    def __init__(self, greeting_service: GreetingService):
        self.greeting_service = greeting_service
        self.last_greeting = None
        self.processed_event = asyncio.Event()

    @EventPattern("user_created")
    async def handle_user_created(self, payload):
        print(f"DEBUG: Handling event {payload}")
        name = payload.get("name")
        self.last_greeting = self.greeting_service.greet(name)
        self.processed_event.set()

@pytest.mark.asyncio
async def test_microservice_controller_di():
    # 1. Setup
    # Re-register services because reset_container cleared them
    container = Container.get_instance()
    container.register(GreetingService)
    container.register(UserController)
    
    transport = MemoryTransport()
    listener = MicroserviceListener(transport, container)
    
    # 2. Start Listener (scans controllers)
    await listener.start()
    
    with open("debug.txt", "w") as f:
        f.write(f"Transport Subscribers: {list(transport.subscribers.keys())}\n")
        f.write(f"Container Providers: {list(container._providers.keys())}\n")
    
    # 3. Publish Event
    await transport.publish("user_created", {"name": "Alice"})
    
    # 4. Wait for processing
    # We need to get the SAME instance of UserController that the listener resolved
    controller = container.resolve(UserController)
    
    with open("debug_ids_test.txt", "w") as f:
        f.write(f"Test Container ID: {id(container)}\n")
        f.write(f"Test Controller ID: {id(controller)}\n")
    
    try:
        await asyncio.wait_for(controller.processed_event.wait(), timeout=1.0)
    except asyncio.TimeoutError:
        pytest.fail("Event was not processed in time")
    
    # 5. Verify Side Effect
    assert controller.last_greeting == "Hello, Alice!"
    
    await listener.stop()
