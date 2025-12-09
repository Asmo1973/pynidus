
import sys
import os
import pytest
from fastapi.testclient import TestClient

# Ensure pynidus is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from pynidus import NidusFactory
from app import AppModule

def test_library_app_flow():
    app = NidusFactory.create(AppModule)
    client = TestClient(app)

    # 1. Get empty list
    response = client.get("/books/")
    assert response.status_code == 200
    assert response.json() == []

    # 2. Create a book
    book_data = {
        "title": "The Hitchhiker's Guide to the Galaxy",
        "author": "Douglas Adams",
        "isbn": "978-0345391803",
        "published_year": 1979
    }
    response = client.post("/books/", json=book_data)
    assert response.status_code == 200
    created_book = response.json()
    assert created_book["title"] == book_data["title"]
    assert created_book["id"] is not None

    # 3. Get list again
    response = client.get("/books/")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == book_data["title"]

    # 4. Get single book
    book_id = created_book["id"]
    response = client.get(f"/books/{book_id}")
    assert response.status_code == 200
    assert response.json()["title"] == book_data["title"]

if __name__ == "__main__":
    test_library_app_flow()
    print("Verification passed!")
