from pynidus import Module
from books.module import BookModule

@Module(
    imports=[BookModule]
)
class AppModule:
    pass
