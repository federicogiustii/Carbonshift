import pika
import time
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
            break  # esce se la coda è vuota

    connection.close()

def global_clock():
    global current_slot
    while True:
        print(f"🕒 SLOT ATTUALE: {current_slot}")
        consume_slot_queue(current_slot)
        current_slot = (current_slot + 1) % 5
        time.sleep(10)
        
if __name__ == "__main__":
    global_clock()