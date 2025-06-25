import argparse
import requests
import random
import time

def generate_profile(mode, slots):
    if mode == "random":
        return [random.randint(1, 10) for _ in range(slots)]
    elif mode == "linear":
        return list(range(1, slots + 1))
    elif mode == "peak":
        mid = slots // 2
        return [i if i <= mid else slots - i + 1 for i in range(slots)]
    elif mode == "camel":
        base = [1, 3, 6, 9, 3, 2, 1, 6, 9, 3]
        if slots != 10:
            raise ValueError("Camel profile requires exactly 10 slot.")
        return base
    else:
        raise ValueError(f"Distribuzione non supportata: {mode}")

def main():
    parser = argparse.ArgumentParser(description="Client generatore di carico probabilistico.")
    parser.add_argument("--mode", type=str, required=True, help="Tipo di distribuzione: random, linear, peak, camel")
    parser.add_argument("--scale", type=int, default=5, help="Fattore moltiplicativo per il carico")
    parser.add_argument("--slots", type=int, default=10, help="Numero di slot virtuali")
    parser.add_argument("--delay", type=float, default=2.0, help="Secondi di pausa tra slot")
    parser.add_argument("--callback", type=str, default="http://localhost:5001/callback", help="URL di callback")
    parser.add_argument("--endpoint", type=str, default="http://localhost:5000/request", help="Endpoint del frontend")

    args = parser.parse_args()
    profile = generate_profile(args.mode, args.slots)

    for slot, weight in enumerate(profile):
        n_requests = args.scale * weight
        print(f"\n[CLIENT] Slot virtuale {slot} → Inviando {n_requests} richieste...")
        for i in range(n_requests):
            msg = {
                "M": f"Richiesta slot {slot} n.{i}",
                "D": random.randint(0, 4),
                "C": args.callback
            }
            try:
                requests.post(args.endpoint, json=msg)
            except Exception as e:
                print(f"[CLIENT] Errore invio: {e}")
        time.sleep(args.delay)

if __name__ == "__main__":
    main()
