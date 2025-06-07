from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Set
import json
import asyncio
import uuid
from datetime import datetime
import structlog
from app.core.config import settings

logger = structlog.get_logger(__name__)

class ConnectionManager:
    """Manages individual WebSocket connections"""
    
    def __init__(self):
        self.connection_id: str = str(uuid.uuid4())
        self.websocket: WebSocket = None
        self.user_id: str = None
        self.connected_at: datetime = None
        self.last_heartbeat: datetime = None
        self.subscriptions: Set[str] = set()

class WebSocketManager:
    """WebSocket connection manager for real-time updates"""
    
    def __init__(self):
        self.connections: Dict[str, ConnectionManager] = {}
        self.topic_subscribers: Dict[str, Set[str]] = {}
        
    async def connect(self, websocket: WebSocket, user_id: str = None):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        
        connection = ConnectionManager()
        connection.websocket = websocket
        connection.user_id = user_id
        connection.connected_at = datetime.utcnow()
        connection.last_heartbeat = datetime.utcnow()
        
        self.connections[connection.connection_id] = connection
        
        logger.info(
            "WebSocket connected",
            connection_id=connection.connection_id,
            user_id=user_id,
            total_connections=len(self.connections)
        )
        
        try:
            await self._handle_connection(connection)
        except WebSocketDisconnect:
            await self._disconnect(connection.connection_id)
        except Exception as e:
            logger.error("WebSocket error", error=str(e), connection_id=connection.connection_id)
            await self._disconnect(connection.connection_id)
    
    async def _handle_connection(self, connection: ConnectionManager):
        """Handle messages from a WebSocket connection"""
        while True:
            try:
                # Wait for message with timeout
                message = await asyncio.wait_for(
                    connection.websocket.receive_text(),
                    timeout=settings.WS_CONNECTION_TIMEOUT
                )
                
                await self._process_message(connection, message)
                
            except asyncio.TimeoutError:
                logger.warning("WebSocket timeout", connection_id=connection.connection_id)
                break
            except WebSocketDisconnect:
                break
    
    async def _process_message(self, connection: ConnectionManager, message: str):
        """Process incoming WebSocket message"""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            
            if message_type == "heartbeat":
                connection.last_heartbeat = datetime.utcnow()
                await self._send_to_connection(connection.connection_id, {
                    "type": "heartbeat_ack",
                    "timestamp": datetime.utcnow().isoformat()
                })
                
            elif message_type == "subscribe":
                topic = data.get("topic")
                if topic:
                    await self._subscribe_to_topic(connection.connection_id, topic)
                    
            elif message_type == "unsubscribe":
                topic = data.get("topic")
                if topic:
                    await self._unsubscribe_from_topic(connection.connection_id, topic)
                    
            else:
                logger.warning("Unknown message type", type=message_type, connection_id=connection.connection_id)
                
        except json.JSONDecodeError:
            logger.error("Invalid JSON message", connection_id=connection.connection_id)
        except Exception as e:
            logger.error("Error processing message", error=str(e), connection_id=connection.connection_id)
    
    async def _subscribe_to_topic(self, connection_id: str, topic: str):
        """Subscribe connection to a topic"""
        if connection_id in self.connections:
            self.connections[connection_id].subscriptions.add(topic)
            
            if topic not in self.topic_subscribers:
                self.topic_subscribers[topic] = set()
            self.topic_subscribers[topic].add(connection_id)
            
            await self._send_to_connection(connection_id, {
                "type": "subscription_confirmed",
                "topic": topic
            })
            
            logger.info("Subscribed to topic", connection_id=connection_id, topic=topic)
    
    async def _unsubscribe_from_topic(self, connection_id: str, topic: str):
        """Unsubscribe connection from a topic"""
        if connection_id in self.connections:
            self.connections[connection_id].subscriptions.discard(topic)
            
            if topic in self.topic_subscribers:
                self.topic_subscribers[topic].discard(connection_id)
                if not self.topic_subscribers[topic]:
                    del self.topic_subscribers[topic]
            
            await self._send_to_connection(connection_id, {
                "type": "unsubscription_confirmed", 
                "topic": topic
            })
            
            logger.info("Unsubscribed from topic", connection_id=connection_id, topic=topic)
    
    async def _disconnect(self, connection_id: str):
        """Disconnect a WebSocket connection"""
        if connection_id in self.connections:
            connection = self.connections[connection_id]
            
            # Remove from all topic subscriptions
            for topic in list(connection.subscriptions):
                await self._unsubscribe_from_topic(connection_id, topic)
            
            # Close WebSocket if still open
            try:
                await connection.websocket.close()
            except:
                pass
            
            # Remove connection
            del self.connections[connection_id]
            
            logger.info(
                "WebSocket disconnected",
                connection_id=connection_id,
                total_connections=len(self.connections)
            )
    
    async def _send_to_connection(self, connection_id: str, data: dict):
        """Send data to a specific connection"""
        if connection_id in self.connections:
            try:
                await self.connections[connection_id].websocket.send_text(
                    json.dumps(data)
                )
            except Exception as e:
                logger.error("Failed to send message", error=str(e), connection_id=connection_id)
                await self._disconnect(connection_id)
    
    async def broadcast_to_topic(self, topic: str, data: dict):
        """Broadcast data to all subscribers of a topic"""
        if topic in self.topic_subscribers:
            message = {
                "type": "broadcast",
                "topic": topic,
                "data": data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            disconnected_connections = []
            for connection_id in self.topic_subscribers[topic]:
                try:
                    await self._send_to_connection(connection_id, message)
                except:
                    disconnected_connections.append(connection_id)
            
            # Clean up disconnected connections
            for connection_id in disconnected_connections:
                await self._disconnect(connection_id)
    
    async def broadcast_to_all(self, data: dict):
        """Broadcast data to all connected clients"""
        message = {
            "type": "global_broadcast",
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        disconnected_connections = []
        for connection_id in list(self.connections.keys()):
            try:
                await self._send_to_connection(connection_id, message)
            except:
                disconnected_connections.append(connection_id)
        
        # Clean up disconnected connections
        for connection_id in disconnected_connections:
            await self._disconnect(connection_id)
    
    async def get_connection_stats(self) -> dict:
        """Get WebSocket connection statistics"""
        return {
            "total_connections": len(self.connections),
            "topics": list(self.topic_subscribers.keys()),
            "topic_subscriber_counts": {
                topic: len(subscribers) 
                for topic, subscribers in self.topic_subscribers.items()
            }
        }
    
    async def cleanup_connections(self):
        """Background task to cleanup stale connections"""
        while True:
            try:
                now = datetime.utcnow()
                stale_connections = []
                
                for connection_id, connection in self.connections.items():
                    # Check if connection hasn't sent heartbeat recently
                    time_since_heartbeat = (now - connection.last_heartbeat).total_seconds()
                    if time_since_heartbeat > settings.WS_HEARTBEAT_INTERVAL * 3:
                        stale_connections.append(connection_id)
                
                # Disconnect stale connections
                for connection_id in stale_connections:
                    logger.info("Cleaning up stale connection", connection_id=connection_id)
                    await self._disconnect(connection_id)
                
                # Wait before next cleanup
                await asyncio.sleep(settings.WS_HEARTBEAT_INTERVAL)
                
            except Exception as e:
                logger.error("Error in connection cleanup", error=str(e))
                await asyncio.sleep(60)  # Wait longer on error
    
    async def disconnect_all(self):
        """Disconnect all WebSocket connections (for shutdown)"""
        for connection_id in list(self.connections.keys()):
            await self._disconnect(connection_id)
