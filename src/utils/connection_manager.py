import asyncio
import json
from logging import Logger
from typing import Dict, List

from fastapi.websockets import WebSocket, WebSocketDisconnect


class ConnectionManager:
    def __init__(self, logger: Logger) -> None:
        self.logger = logger
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, session_id: str) -> None:
        await websocket.accept()

        if session_id not in self.active_connections:
            self.active_connections[session_id] = []

        self.active_connections[session_id].append(websocket)

    def disconnect(self, websocket: WebSocket, session_id: str) -> None:
        if session_id not in self.active_connections:
            return

        self.active_connections[session_id] = [connection for connection in self.active_connections[session_id] if connection != websocket]

        if not self.active_connections[session_id]:
            del self.active_connections[session_id]

    async def broadcast(self, session_id: str, message: dict) -> None:
        if session_id not in self.active_connections:
            return

        for websocket in self.active_connections[session_id]:
            try:
                await websocket.send_text(json.dumps(message, ensure_ascii=False))
            except (RuntimeError, WebSocketDisconnect):
                self.disconnect(websocket, session_id)

    async def ping(self, websocket: WebSocket, session_id: str) -> None:
        while True:
            await asyncio.sleep(30)
            try:
                await websocket.send_text("ping")
            except WebSocketDisconnect:
                self.disconnect(websocket, session_id)
                break
            except Exception as e:
                self.logger.error(f'Error during ping in the session "{session_id}": {e}')
                self.disconnect(websocket, session_id)
                break
