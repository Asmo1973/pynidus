from pynidus import Module
from .controller import BookController
from .service import BookService

@Module(
    controllers=[BookController],
    providers=[BookService],
)
class BookModule:
    pass
