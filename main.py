import asyncio

from src.flappy import Flappy

if __name__ == "__main__":
    apiURL = "http://127.0.0.1:8000"
    asyncio.run(Flappy().start(apiURL))
