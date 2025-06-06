import pika
import time
import json

def clock_master(tick_interval=10):
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()
    channel.queue_declare(queue="tick_queue")

    tick_count = 0
    while True:
        message = {"tick": tick_count}
        channel.basic_publish(exchange="", routing_key="tick_queue", body=json.dumps(message))
        print(f"🕰️  [CLOCK] Tick {tick_count} inviato")
        tick_count += 1
        time.sleep(tick_interval)

if __name__ == "__main__":
    clock_master()
