
from kafka import KafkaProducer
import json
import time
from .services import fetch_and_cache_price
import environ
env= environ.Env()
environ.Env.read_env()
producer = KafkaProducer(
    bootstrap_servers= env('KAFKA_BOOTSTRAP_SERVERS'),
    value_serializer=lambda m: json.dumps(m).encode('utf-8'),
)

WATCHED_SYMBOLS=["RELIANCE.NS","M&M.NS","TCS.NS"]

def run_price_producer():
    for symbol in WATCHED_SYMBOLS:
        value=fetch_and_cache_price(symbol)
        message={"symbol":symbol,"price":value,"timestamp":time.time()}
        producer.send(topic="price-updates",value=message)
    producer.flush()
