import asyncio
import json
from typing import Dict, Any, List, Callable, Optional
from datetime import datetime
from collections import defaultdict

class MessageBus:
    """
    Event-driven message bus for inter-agent communication
    Enables autonomous agents to communicate and coordinate
    """
    
    def __init__(self):
        self.subscribers = defaultdict(list)
        self.message_history = []
        self.message_queue = asyncio.Queue()
        self.running = False
        self.stats = {
            'messages_sent': 0,
            'messages_processed': 0,
            'active_subscribers': 0
        }
    
    async def start(self):
        """Start the message bus"""
        self.running = True
        print("🚌 Message Bus: Starting communication layer...")
        
        # Start message processing loop
        asyncio.create_task(self._process_messages())
    
    async def stop(self):
        """Stop the message bus"""
        self.running = False
        print("🛑 Message Bus: Stopping communication layer...")
    
    async def publish(self, channel: str, message: Dict[str, Any]):
        """Publish a message to a channel"""
        
        message_envelope = {
            'id': f"MSG-{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            'channel': channel,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'processed': False
        }
        
        await self.message_queue.put(message_envelope)
        self.stats['messages_sent'] += 1
        
        print(f"📤 Published to {channel}: {message.get('type', 'message')}")
    
    async def subscribe(self, channel: str, callback: Callable[[Dict[str, Any]], None]):
        """Subscribe to a channel with a callback function"""
        
        self.subscribers[channel].append(callback)
        self.stats['active_subscribers'] = sum(len(subs) for subs in self.subscribers.values())
        
        print(f"📧 New subscriber to {channel}")
    
    async def _process_messages(self):
        """Process messages from the queue"""
        
        while self.running:
            try:
                # Get message from queue with timeout
                message_envelope = await asyncio.wait_for(
                    self.message_queue.get(), timeout=1.0
                )
                
                await self._deliver_message(message_envelope)
                self.stats['messages_processed'] += 1
                
            except asyncio.TimeoutError:
                # No messages to process, continue
                continue
            except Exception as e:
                print(f"❌ Message processing error: {e}")
    
    async def _deliver_message(self, message_envelope: Dict[str, Any]):
        """Deliver message to all subscribers of the channel"""
        
        channel = message_envelope['channel']
        message = message_envelope['message']
        
        # Store in history
        self.message_history.append(message_envelope)
        
        # Deliver to subscribers
        for callback in self.subscribers[channel]:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(message)
                else:
                    callback(message)
            except Exception as e:
                print(f"❌ Delivery error to {channel}: {e}")
        
        message_envelope['processed'] = True
    
    def get_channel_history(self, channel: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get message history for a specific channel"""
        
        channel_messages = [
            msg for msg in self.message_history 
            if msg['channel'] == channel
        ]
        
        return channel_messages[-limit:]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get message bus statistics"""
        
        return {
            **self.stats,
            'active_channels': list(self.subscribers.keys()),
            'queue_size': self.message_queue.qsize(),
            'history_size': len(self.message_history)
        }


class AgentCommunicationProtocol:
    """
    Protocol for structured agent-to-agent communication
    """
    
    def __init__(self, agent_name: str, message_bus: MessageBus):
        self.agent_name = agent_name
        self.message_bus = message_bus
        self.received_messages = []
    
    async def send_request(self, target_agent: str, request_type: str, 
                          data: Dict[str, Any]) -> str:
        """Send a request to another agent"""
        
        request_id = f"REQ-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        
        message = {
            'type': 'agent_request',
            'request_id': request_id,
            'from_agent': self.agent_name,
            'to_agent': target_agent,
            'request_type': request_type,
            'data': data,
            'requires_response': True
        }
        
        await self.message_bus.publish(f"agent.{target_agent}", message)
        return request_id
    
    async def send_response(self, request_id: str, target_agent: str, 
                           response_data: Dict[str, Any]):
        """Send a response to an agent request"""
        
        message = {
            'type': 'agent_response',
            'request_id': request_id,
            'from_agent': self.agent_name,
            'to_agent': target_agent,
            'response_data': response_data
        }
        
        await self.message_bus.publish(f"agent.{target_agent}", message)
    
    async def broadcast_event(self, event_type: str, event_data: Dict[str, Any]):
        """Broadcast an event to all interested agents"""
        
        message = {
            'type': 'agent_event',
            'event_type': event_type,
            'from_agent': self.agent_name,
            'event_data': event_data,
            'timestamp': datetime.now().isoformat()
        }
        
        await self.message_bus.publish("events", message)
    
    async def listen_for_messages(self):
        """Start listening for messages directed to this agent"""
        
        await self.message_bus.subscribe(
            f"agent.{self.agent_name}", 
            self._handle_incoming_message
        )
    
    async def _handle_incoming_message(self, message: Dict[str, Any]):
        """Handle incoming messages for this agent"""
        
        self.received_messages.append(message)
        
        if message['type'] == 'agent_request':
            await self._process_agent_request(message)
        elif message['type'] == 'agent_response':
            await self._process_agent_response(message)
    
    async def _process_agent_request(self, message: Dict[str, Any]):
        """Process requests from other agents"""
        
        print(f"📨 {self.agent_name} received request: {message['request_type']} from {message['from_agent']}")
        
        # Override in specific agent implementations
        # For now, send a generic acknowledgment
        await self.send_response(
            message['request_id'],
            message['from_agent'],
            {'status': 'received', 'message': 'Request acknowledged'}
        )
    
    async def _process_agent_response(self, message: Dict[str, Any]):
        """Process responses from other agents"""
        
        print(f"📬 {self.agent_name} received response for request {message['request_id']}")


class KnowledgeBase:
    """
    Shared knowledge base for agents to store and retrieve information
    """
    
    def __init__(self):
        self.knowledge_store = {}
        self.access_log = []
        self.version_history = {}
    
    async def store_knowledge(self, key: str, value: Any, agent_name: str = None):
        """Store knowledge in the shared base"""
        
        # Version control
        if key in self.knowledge_store:
            if key not in self.version_history:
                self.version_history[key] = []
            self.version_history[key].append({
                'value': self.knowledge_store[key],
                'timestamp': datetime.now().isoformat(),
                'agent': agent_name
            })
        
        self.knowledge_store[key] = value
        
        self.access_log.append({
            'action': 'store',
            'key': key,
            'agent': agent_name,
            'timestamp': datetime.now().isoformat()
        })
        
        print(f"🧠 Knowledge stored: {key} by {agent_name}")
    
    async def retrieve_knowledge(self, key: str, agent_name: str = None) -> Optional[Any]:
        """Retrieve knowledge from the shared base"""
        
        self.access_log.append({
            'action': 'retrieve',
            'key': key,
            'agent': agent_name,
            'timestamp': datetime.now().isoformat()
        })
        
        value = self.knowledge_store.get(key)
        if value:
            print(f"🧠 Knowledge retrieved: {key} by {agent_name}")
        
        return value
    
    async def query_knowledge(self, pattern: str, agent_name: str = None) -> Dict[str, Any]:
        """Query knowledge using patterns"""
        
        matching_keys = [
            key for key in self.knowledge_store.keys()
            if pattern.lower() in key.lower()
        ]
        
        result = {key: self.knowledge_store[key] for key in matching_keys}
        
        self.access_log.append({
            'action': 'query',
            'pattern': pattern,
            'results_count': len(result),
            'agent': agent_name,
            'timestamp': datetime.now().isoformat()
        })
        
        return result
    
    def get_knowledge_stats(self) -> Dict[str, Any]:
        """Get statistics about knowledge base usage"""
        
        return {
            'total_items': len(self.knowledge_store),
            'total_accesses': len(self.access_log),
            'agents_using': len(set(log['agent'] for log in self.access_log if log['agent'])),
            'most_accessed_keys': self._get_most_accessed_keys()
        }
    
    def _get_most_accessed_keys(self) -> List[str]:
        """Get the most frequently accessed knowledge items"""
        
        key_counts = {}
        for log in self.access_log:
            if 'key' in log:
                key_counts[log['key']] = key_counts.get(log['key'], 0) + 1
        
        return sorted(key_counts.items(), key=lambda x: x[1], reverse=True)[:5]
