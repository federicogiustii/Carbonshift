from flask import Flask, request

app = Flask(__name__)

@app.route("/callback", methods=["POST"])
def callback():
    data = request.json
    print(f"""[CLIENT] Callback ricevuta:
    • Echo: {data["echo"]}
    • Strategia: {data["strategy"]}
    • Slot eseguito: {data["slot_executed"]}
""")
    return "Callback ricevuta", 200

if __name__ == "__main__":
    app.run(port=5001)
