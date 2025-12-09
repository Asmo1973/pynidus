import sys
import os

# Ensure pynidus is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

import uvicorn
from pynidus import NidusFactory
from app import AppModule

def main():
    app = NidusFactory.create(AppModule)
    print("Starting Library App on http://localhost:3000")
    uvicorn.run(app, host="0.0.0.0", port=3000)

if __name__ == "__main__":
    main()
