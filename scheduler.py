import pika
import json
import random

def carbon_shift_strategy():
    return random.choice(["low", "medium", "high"])

def consume_ingress_queue(channel):
    messages = []
    while True:
        method, properties, body = channel.basic_get(queue="ingress_queue", auto_ack=True)
        if body:
            data = json.loads(body)
            messages.append(data)
        else:
            break
    return messages

def flush_to_slot_queues(channel, messages):
    for data in messages:
        slot = random.randint(0, 4)
        strategy = carbon_shift_strategy()
        data["slot"] = slot
        data["strategy"] = strategy

        slot_queue = f"slot_{slot}"
        channel.queue_declare(queue=slot_queue)
        channel.basic_publish(exchange="", routing_key=slot_queue, body=json.dumps(data))

        print(f"""✅ [SCHEDULER] Richiesta smistata:
    • Messaggio: {data["M"]}
    • Strategia: {strategy}
    • Slot assegnato: {slot}
""")

def listen_for_ticks():
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()

    channel.queue_declare(queue="ingress_queue")  # Assicura che esista

    # Dichiara exchange fanout tick_exchange
    channel.exchange_declare(exchange="tick_exchange", exchange_type="fanout")
    # Crea coda temporanea esclusiva per questo consumer
    result = channel.queue_declare(queue="", exclusive=True)
    queue_name = result.method.queue
    # Bind coda temporanea all'exchange fanout
    channel.queue_bind(exchange="tick_exchange", queue=queue_name)

    def on_tick(ch, method, properties, body):
        tick = json.loads(body)["tick"]
        print(f"⏰ [SCHEDULER] Tick ricevuto: {tick}")
        requests = consume_ingress_queue(channel)
        if requests:
            print(f"📦 [SCHEDULER] Prelevo {len(requests)} richieste da 'ingress_queue'")
            flush_to_slot_queues(channel, requests)
        else:
            print("💤 [SCHEDULER] Nessuna richiesta da elaborare.")

    print("⏱️ [SCHEDULER] In ascolto dei tick...")
    channel.basic_consume(queue=queue_name, on_message_callback=on_tick, auto_ack=True)
    channel.start_consuming()

if __name__ == "__main__":
    listen_for_ticks()
