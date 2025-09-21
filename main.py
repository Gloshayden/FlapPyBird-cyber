import asyncio

from src.flappy import Flappy

if __name__ == "__main__":
    websocketURL = "ws://127.0.0.1:8000"
    asyncio.run(Flappy().start(websocketURL))
