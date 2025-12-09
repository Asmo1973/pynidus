from fastapi import Body
from pynidus import Controller, Get, Post
from .service import BookService
from .schemas import CreateBookDto

@Controller("/books")
class BookController:
    def __init__(self, book_service: BookService):
        self.book_service = book_service

    @Get("/")
    def find_all(self):
        return self.book_service.find_all()

    @Post("/")
    def create(self, create_book_dto: CreateBookDto):
        return self.book_service.create(create_book_dto)

    @Get("/{book_id}")
    def find_one(self, book_id: int):
        book = self.book_service.find_one(book_id)
        if not book:
            return {"error": "Book not found"}
        return book
