import asyncio
import json
import logging
import sys
from typing import Any, Callable, Dict, Optional

from src.infrastructure.logging_config import get_logger

try: 
    from confluent_kafka import Consumer, KafkaException, Producer
    from confluent_kafka.schema_registry import SchemaRegistryClient
    from confluent_kafka.schema_registry.avro import (
        AvroDeserializer,
        AvroSerializer,
    )
    from confluent_kafka.serialization import (
        MessageField,
        SerializationContext,
        StringSerializer,
    )
except ImportError as e: 
    logger = get_logger(__name__, component="infrastructure")    
    logger.critical(f"CRITICAL ERROR: confluent-kafka is required for production use: {e}")    
    logger.critical("Install required dependencies: pip install confluent-kafka")    
    logger.critical("Kafka event bus functionality will be disabled") 
    raise ImportError(f"Missing required dependency for Kafka event bus: confluent-kafka. Install with 'pip install confluent-kafka'") from e

from src.domain.events.domain_events import DomainEvent

logger = get_logger(__name__, component="infrastructure")
    
class KafkaEventBus: 
    def __init__(self, bootstrap_servers: str, schema_registry_url: str, client_id: str="teddy-bear-app") -> None: 
        self.bootstrap_servers = bootstrap_servers        
        self.schema_registry_url = schema_registry_url        
        self.client_id = client_id        
        self.connected = True        
        self.connection_timeout = 5  # 5 seconds timeout        
        self.producer: Optional[Producer] = None        
        self.consumers: Dict[str, Consumer] = {}        
        self.avro_serializers: Dict[str, AvroSerializer] = {}        
        self.avro_deserializers: Dict[str, AvroDeserializer] = {}        
        self.string_serializer = StringSerializer("utf_8")        
        self.handlers: Dict[str, Callable[[DomainEvent], Any]] = {}        
        self.running = False        
        self.producer_config = {            
            "bootstrap.servers": self.bootstrap_servers,            
            "client.id": self.client_id,        
        }        
        self.consumer_config = {            
            "bootstrap.servers": self.bootstrap_servers,            
            "group.id": f"{self.client_id}-group",            
            "auto.offset.reset": "earliest",        
        }        
        self.schema_registry_client = SchemaRegistryClient({"url": self.schema_registry_url})    
    
    async def _attempt_connection(self) -> None:        
        self.producer = Producer(self.producer_config)    
        
    async def publish(self, event: DomainEvent) -> None:        
        """Publish message to Kafka"""        
        if not self.connected:            
            raise ConnectionError("Kafka not connected")        
        if not self.producer:            
            await self._attempt_connection()        
        topic = event.__class__.__name__.lower()  # Topic name from event class name        
        if topic not in self.avro_serializers:            
                # Create mock schema for testing            
                schema_str = json.dumps({                
                    "type": "record",                
                    "name": event.__class__.__name__,                
                    "fields": [                    
                        {"name": "event_id", "type": "string"},                    
                        {"name": "timestamp", "type": "string"},                
                    ]            
                })            
                self.avro_serializers[topic] = AvroSerializer(                
                    schema_registry_client=self.schema_registry_client,                
                    schema_str=schema_str,                
                    to_dict=self._event_to_dict,            
                )        
        try:            
            if self.producer:                
                    self.producer.produce(                    
                        topic=topic,                    
                        key=self.string_serializer(str(getattr(event, 'event_id', 'default'))),                    
                        value=self.avro_serializers[topic](event, SerializationContext(topic, MessageField.VALUE)),                    
                        on_delivery=self._delivery_report,                
                    )                
                    self.producer.poll(0)        
        except Exception as e:            
            logger.error(f"Failed to produce message to topic {topic}: {e}")    
        
    def subscribe(self, event_type: type[DomainEvent], handler: Callable[[DomainEvent], Any]) -> None:        
            topic = event_type.__name__.lower()        
            self.handlers[topic] = handler        
            if topic not in self.consumers:            
                consumer = Consumer(self.consumer_config)            
                consumer.subscribe([topic])            
                self.consumers[topic] = consumer            
                # Initialize deserializer for this topic            
                if topic not in self.avro_deserializers:                
                    self.avro_deserializers[topic] = AvroDeserializer(                    
                        schema_registry_client=self.schema_registry_client,                    
                        schema_str=None,                    
                        from_dict=lambda obj, ctx: event_type(**obj) if isinstance(obj, dict) else obj                
                    )    
        
    async def start_consuming(self) -> None:        
            self.running = True        
            while self.running:            
                for topic, consumer in self.consumers.items():                
                    try:                    
                        msg = consumer.poll(timeout=1.0)                    
                        if msg is None:                        
                            continue                    
                        if hasattr(msg, 'error') and msg.error():                        
                            if hasattr(KafkaException, '_PARTITION_EOF') and msg.error().code() == KafkaException._PARTITION_EOF:                            
                                continue                        
                            else:                            
                                logger.error(f"Consumer error: {msg.error()}")                            
                                break                    
                        deserializer = self.avro_deserializers.get(topic)                    
                        if deserializer:                        
                            event = deserializer(msg.value(), SerializationContext(msg.topic(), MessageField.VALUE))                        
                            if event and topic in self.handlers:                            
                                await self.handlers[topic](event)                    
                        else:                        
                            logger.warning(f"No deserializer found for topic {topic}")                
                    except Exception as e:                    
                        logger.error(f"Failed to process message: {e}")
                        continue            
                await asyncio.sleep(0.1)    
        
    def stop_consuming(self) -> None:        
        self.running = False        
        for consumer in self.consumers.values():            
            consumer.close()    
    
    def _delivery_report(self, err: Optional[Any], msg: Any) -> None:        
        if err is not None:            
            logger.error(f"Message delivery failed: {err}")        
        else:            
            logger.debug(f"Message delivered to {msg.topic()} [{msg.partition()}] @ offset {msg.offset()}")    
    
    def _event_to_dict(self, event: DomainEvent, ctx: SerializationContext) -> Dict[str, Any]:        
        # Convert dataclass to dictionary for Avro serialization        
        if hasattr(event, '__dict__'):            
            return event.__dict__        
        else:            
            return {"event_type": type(event).__name__}
            
    def __del__(self):
        """Cleanup resources when instance is destroyed"""
        try:
            if hasattr(self, 'running') and self.running:
                self.stop_consuming()
        except Exception:
            # Ignore errors during cleanup
            pass