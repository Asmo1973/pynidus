from pynidus import Injectable
from typing import List, Dict
from .schemas import Book, CreateBookDto

@Injectable()
class BookService:
    def __init__(self):
        self.books: Dict[int, Book] = {}
        self.id_counter = 1

    def create(self, book_dto: CreateBookDto) -> Book:
        book = Book(id=self.id_counter, **book_dto.model_dump())
        self.books[self.id_counter] = book
        self.id_counter += 1
        return book

    def find_all(self) -> List[Book]:
        return list(self.books.values())

    def find_one(self, book_id: int) -> Optional[Book]:
        return self.books.get(book_id)
