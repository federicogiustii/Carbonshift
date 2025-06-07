import pika
import json
import requests

current_slot = 0
TOTAL_SLOTS = 5
QUEUE_NAMES = [f"slot_queue_{i}" for i in range(TOTAL_SLOTS)]

def service_s_execute(slot, request_data):
    result = {
        "echo": request_data["M"],
        "strategy": request_data["strategy"],
        "slot_executed": slot
    }
    print(f"[SERVICE] Esecuzione slot {slot}: {result}")
    try:
        requests.post(request_data["C"], json=result)
    except Exception as e:
        print(f"Errore nella callback: {e}")

def consume_slot_queue(channel, queue_name, slot):
    while True:
        method, properties, body = channel.basic_get(queue=queue_name, auto_ack=True)
        if body:
            request_data = json.loads(body)
            service_s_execute(slot, request_data)
        else:
            break

def listen_to_ticks():
    global current_slot
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()

    # Dichiara exchange per i tick
    channel.exchange_declare(exchange="tick_exchange", exchange_type="fanout")

    # Dichiara exchange per i messaggi negli slot
    channel.exchange_declare(exchange="slot_exchange", exchange_type="topic")

    # Crea tutte le code slot e le collega ai rispettivi topic
    for i in range(TOTAL_SLOTS):
        queue_name = f"slot_queue_{i}"
        channel.queue_declare(queue=queue_name)
        channel.queue_bind(exchange="slot_exchange", queue=queue_name, routing_key=f"slot.{i}")

    # Coda temporanea per i tick
    tick_queue = channel.queue_declare(queue="", exclusive=True).method.queue
    channel.queue_bind(exchange="tick_exchange", queue=tick_queue)

    def on_tick(ch, method, properties, body):
        global current_slot
        tick_data = json.loads(body)
        print(f"[SERVICE] Ricevuto tick {tick_data['tick']} → Slot {current_slot}")
        consume_slot_queue(channel, f"slot_queue_{current_slot}", current_slot)
        current_slot = (current_slot + 1) % TOTAL_SLOTS

    channel.basic_consume(queue=tick_queue, on_message_callback=on_tick, auto_ack=True)
    print("[SERVICE] In ascolto dei tick...")
    channel.start_consuming()

if __name__ == "__main__":
    listen_to_ticks()
