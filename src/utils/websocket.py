import asyncio

import websocket
from websocket import BrokenPipeError


class WebSocketClient:
    def __init__(self, uri):
        self.uri = uri
        self.ws = None

    def connect(self):
        self.ws = websocket.WebSocket()
        try:
            self.ws.connect(self.uri, timeout=480)
        except Exception as e:
            print(f"Failed to connect to {self.uri}: {e}")
            self.ws = None

    def respond(self, message):
        if self.ws is not None:
            try:
                self.ws.send(message)
            except BrokenPipeError:
                self.connect()
                self.ws.send(message)
            return self.ws.recv()
        return None

    async def send(self, message):
        if self.ws is not None:
            try:
                self.ws.send(message)
            except BrokenPipeError:
                self.connect()
                self.ws.send(message)
            return asyncio.sleep(2)

    def receive(self):
        if self.ws is not None:
            return self.ws.recv()

    def close(self):
        if self.ws is not None:
            self.ws.close()
            self.ws = None
        return
