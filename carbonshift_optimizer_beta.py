from ortools.sat.python import cp_model
import math
from statistics import mean

def assign_requests_carbonshift(requests, strategies, carbon_intensities, delta, epsilon, beta=None):
    '''
    Funzione che implementa lo scheduling Carbonshift con supporto a blocchi configurabili (β).

    Parametri:
    - requests: lista di richieste, ciascuna con 'id' e 'deadline'
    - strategies: lista di strategie disponibili, ognuna con 'name', 'error' e 'duration'
    - carbon_intensities: lista delle emissioni previste per ogni slot temporale
    - delta: numero totale di slot temporali futuri (es. 48 per 24 ore a slot da 30 minuti)
    - epsilon: soglia massima per l’errore medio accettabile
    - beta: numero di blocchi. Se None o ≥ len(requests), ogni richiesta è trattata singolarmente

    Ritorna:
    - assignment: dizionario {request_id: (slot, strategy_name)}
    '''

    # 🎯 BLOCCO 1 - Divisione delle richieste in blocchi (β)
    if beta is None or beta >= len(requests):
        # Versione base → ogni richiesta è un blocco separato
        blocks = [[req] for req in requests]
    else:
        # Versione scalabile → ordinamento per deadline e suddivisione in β gruppi
        sorted_requests = sorted(requests, key=lambda r: r["deadline"])
        group_size = math.ceil(len(requests) / beta)
        blocks = [sorted_requests[i:i + group_size] for i in range(0, len(sorted_requests), group_size)]

    model = cp_model.CpModel()
    B = list(range(len(blocks)))              # Indici blocchi
    S = list(range(len(strategies)))          # Indici strategie
    T = list(range(delta))                    # Indici time slot

    # 🔁 Mappatura richiesta → blocco
    req_to_block = {}
    for b, group in enumerate(blocks):
        for req in group:
            req_to_block[req["id"]] = b

    # 🔒 Vincolo: ogni blocco ha deadline = min delle deadline interne
    block_deadlines = [min(req["deadline"] for req in group) for group in blocks]

    # 🔧 Variabili decisionali binarie: x[b,s,t] = 1 se blocco b è assegnato alla strategia s nello slot t
    x = {}
    for b in B:
        for s in S:
            for t in T:
                # Vincolo: slot t deve rispettare la deadline del blocco
                if t <= block_deadlines[b]:
                    x[(b, s, t)] = model.NewBoolVar(f"x_{b}_{s}_{t}")

    # 🔒 Vincolo 1: ogni blocco deve essere assegnato ad una sola combinazione (slot, strategia)
    for b in B:
        model.AddExactlyOne(x[(b, s, t)] for s in S for t in T if (b, s, t) in x)

    # 🔒 Vincolo 2: errore medio totale ≤ epsilon * numero_blocchi
    # Regola: somma degli errori pesati per le strategie usate deve essere entro soglia
    total_error_expr = []
    for b in B:
        for s in S:
            for t in T:
                if (b, s, t) in x:
                    total_error_expr.append(x[(b, s, t)] * strategies[s]["error"])
    model.Add(sum(total_error_expr) <= epsilon * len(blocks))

    # 🎯 Obiettivo: minimizzare somma(CO₂[t] * durata strategia s) su tutti i blocchi assegnati
    objective_terms = []
    for b in B:
        for s in S:
            for t in T:
                if (b, s, t) in x:
                    objective_terms.append(
                        x[(b, s, t)] * carbon_intensities[t] * strategies[s]["duration"]
                    )
    model.Minimize(sum(objective_terms))

    # 🧠 Risoluzione
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    # Se non esiste soluzione ammissibile, segnala errore
    if status not in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        raise RuntimeError("No feasible assignment found")

    # ⏱️ Output finale: ogni richiesta eredita lo slot e la strategia assegnata al suo blocco
    assignment = {}
    for b in B:
        for s in S:
            for t in T:
                if (b, s, t) in x and solver.BooleanValue(x[(b, s, t)]):
                    for req in blocks[b]:
                        assignment[req["id"]] = (t, strategies[s]["name"])

    return assignment
