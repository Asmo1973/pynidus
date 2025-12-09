import sys
import os

# Ensure pynidus is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from pynidus import NidusFactory
from app import AppModule

def main():
    print("Starting Library App...")
    # This will read configuration from env vars automatically
    NidusFactory.listen(AppModule)

if __name__ == "__main__":
    main()
