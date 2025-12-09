from pydantic import BaseModel
from typing import Optional

class CreateBookDto(BaseModel):
    title: str
    author: str
    isbn: str
    published_year: int

class Book(CreateBookDto):
    id: int
