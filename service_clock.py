import pika
import json
import requests

current_slot = 0

def service_s_execute(slot, request_data):
    result = {
        "echo": request_data["M"],
        "strategy": request_data["strategy"],
        "slot_executed": slot
    }
    print(f"⚙️  [SERVICE] Esecuzione slot {slot}: {result}")
    try:
        requests.post(request_data["C"], json=result)
    except Exception as e:
        print(f"❌ Errore nella callback: {e}")

def consume_slot_queue(slot):
    queue_name = f"slot_{slot}"
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()
    channel.queue_declare(queue=queue_name)

    while True:
        method, properties, body = channel.basic_get(queue=queue_name, auto_ack=True)
        if body:
            request_data = json.loads(body)
            service_s_execute(slot, request_data)
        else:
            break

    connection.close()

def listen_to_ticks():
    global current_slot
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()

    # Dichiara exchange fanout tick_exchange
    channel.exchange_declare(exchange="tick_exchange", exchange_type="fanout")
    # Crea coda temporanea esclusiva per questo consumer
    result = channel.queue_declare(queue="", exclusive=True)
    queue_name = result.method.queue
    # Bind coda temporanea all'exchange fanout
    channel.queue_bind(exchange="tick_exchange", queue=queue_name)

    def on_tick(ch, method, properties, body):
        global current_slot
        tick_data = json.loads(body)
        print(f"⏱️  [SERVICE] Ricevuto tick {tick_data['tick']} → Slot {current_slot}")
        consume_slot_queue(current_slot)
        current_slot = (current_slot + 1) % 5

    channel.basic_consume(queue=queue_name, on_message_callback=on_tick, auto_ack=True)
    print("🎧 [SERVICE] In ascolto dei tick...")
    channel.start_consuming()

if __name__ == "__main__":
    listen_to_ticks()
