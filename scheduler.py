import pika
import json
import random

def carbon_shift_strategy():
    return random.choice(["low", "medium", "high"])

def scheduler():
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()
    channel.queue_declare(queue="ingress_queue")

    def callback(ch, method, properties, body):
        data = json.loads(body)
        slot = random.randint(0, 4)  # 0-4
        strategy = carbon_shift_strategy()
        data["slot"] = slot
        data["strategy"] = strategy

        slot_queue_name = f"slot_{slot}"
        channel.queue_declare(queue=slot_queue_name)
        channel.basic_publish(exchange="", routing_key=slot_queue_name, body=json.dumps(data))

        print(f"""✅ [SCHEDULER] Richiesta assegnata:
    • Messaggio: {data["M"]}
    • Strategia: {strategy}
    • Slot assegnato: {slot}
""")

    channel.basic_consume(queue="ingress_queue", on_message_callback=callback, auto_ack=True)
    print("🎯 [SCHEDULER] In ascolto su 'ingress_queue'...")
    channel.start_consuming()

if __name__ == "__main__":
    scheduler()