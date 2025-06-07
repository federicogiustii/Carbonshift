# CarbonShift - Prototipo asincrono carbon-aware

## 🧭 Obiettivo del sistema

Il prototipo implementa un sistema asincrono ispirato alla logica CarbonShift, che assegna dinamicamente richieste a slot temporali futuri e strategie di esecuzione, ottimizzando il compromesso tra:
- Minimizzazione dell'impatto carbonico (emissioni CO₂)
- Rispetto delle deadline delle richieste
- Controllo della qualità del risultato (errore medio sotto soglia)

---

## 🧩 Componenti principali

### 1. Client (`client.py`)
- Invia richieste asincrone `(M, D, C)`:
  - `M`: messaggio
  - `D`: deadline
  - `C`: URL per il callback

### 2. Frontend (`frontend.py`)
- Interfaccia per simulare o inviare richieste al sistema

### 3. Global Clock (`clock_master.py`, `service_clock.py`)
- Simula l’avanzamento temporale tramite tick inviati a `tick_exchange`

### 4. Scheduler (`scheduler.py`)
- Riceve i tick
- Preleva richieste da `ingress_queue`
- Carica:
  - `strategies.csv`: strategie disponibili
  - `co2.csv`: emissioni CO₂ previste per slot
  - `scheduler_config.csv`: parametri `beta`, `epsilon`
- Ottimizza l’assegnamento tramite `assign_requests_carbonshift`
- Pubblica le richieste su `slot_exchange`

### 5. Ottimizzatore (`carbonshift_optimizer_beta.py`)
- Algoritmo CP-SAT (Google OR-Tools)
- Gestione di blocchi (`beta`)
- Rispetto di deadline e errore medio (`epsilon`)
- Minimizzazione: somma(CO₂[t] × durata strategia)

### 6. Service (`client_callback.py`)
- Esegue le richieste assegnate al tick corrente
- Risponde al client via callback

---

## 🗂️ File CSV di configurazione

### `strategies.csv`
```csv
name,error,duration
low,6,1
medium,4,15
high,0,20
```

### `co2.csv`
```csv
100,75,120,110,70
```

### `scheduler_config.csv`
```csv
parameter,value
epsilon,3
beta,2
```

---

## ▶️ Esecuzione

### 1. Avvia RabbitMQ
```bash
sudo service rabbitmq-server start
```

### 2. Esegui i componenti
```bash
python clock_master.py
python scheduler.py
python client_callback.py
python client.py
```

---

## 📦 Dipendenze

- Python 3.8+
- Librerie:
  - `pika` (RabbitMQ)
  - `ortools` (ottimizzazione)
```bash
pip install pika ortools
```

---

## ✅ Stato

✔️ Sistema asincrono, configurabile via CSV, fedele al modello CarbonShift (sia base che scalabile).
