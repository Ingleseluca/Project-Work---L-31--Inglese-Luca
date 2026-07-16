import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta


# Impostiamo un "seed" per rendere i dati casuali ma riproducibili ad ogni esecuzione
np.random.seed(42)

# Configurazione parametri
NUM_CLIENTI = 350
NUM_FORNITORI = 50
NUM_OPERATORI = 80
NUM_RICHIESTE = 550

ZONE = ['Centro', 'Nord-Est', 'Nord-Ovest', 'Sud', 'Isole']
CATEGORIE = ['Consegne Rapide', 'Pulizie Domestiche', 'Manutenzione Casa', 'Assistenza Personale']
STATI_RICHIESTA = ['Completata', 'Completata', 'Completata', 'Annullata', 'In Corso'] # Più probabilità per 'Completata'

# 1. GENERAZIONE CLIENTI
print("Generazione tabella Clienti...")
clienti_data = {
    'cliente_id': [f"CLI_{str(i).zfill(4)}" for i in range(1, NUM_CLIENTI + 1)],
    'zona': np.random.choice(ZONE, size=NUM_CLIENTI, p=[0.3, 0.2, 0.2, 0.2, 0.1]),
    'data_iscrizione': [
        (datetime(2025, 1, 1) + timedelta(days=int(np.random.randint(0, 365)))).strftime('%Y-%m-%d')
        for _ in range(NUM_CLIENTI)
    ]
}
df_clienti = pd.DataFrame(clienti_data)
df_clienti.to_csv('data/clienti.csv', index=False)

# 2. GENERAZIONE FORNITORI
print("Generazione tabella Fornitori...")
nomi_fornitori = [
    "Alpha Servizi", "Beta Express", "Gamma Cleaning", "Delta Repair", "Apex Taskers",
    "EcoClean", "SgombraTutto", "ProntoIntervento", "FastDelivery", "EasyHome"
]
fornitori_data = {
    'fornitore_id': [f"FOR_{str(i).zfill(3)}" for i in range(1, NUM_FORNITORI + 1)],
    'nome': [f"{np.random.choice(nomi_fornitori)} #{i}" for i in range(1, NUM_FORNITORI + 1)],
    'categoria_servizio': np.random.choice(CATEGORIE, size=NUM_FORNITORI),
    'zona_operativa': np.random.choice(ZONE, size=NUM_FORNITORI)
}
df_fornitori = pd.DataFrame(fornitori_data)
df_fornitori.to_csv('data/fornitori.csv', index=False)

# 3. GENERAZIONE OPERATORI
print("Generazione tabella Operatori...")
operatori_data = {
    'operatore_id': [f"OPE_{str(i).zfill(3)}" for i in range(1, NUM_OPERATORI + 1)],
    'zona_competenza': np.random.choice(ZONE, size=NUM_OPERATORI),
    'tipo_attivita': np.random.choice(['Standard', 'Premium'], size=NUM_OPERATORI, p=[0.8, 0.2])
}
df_operatori = pd.DataFrame(operatori_data)
df_operatori.to_csv('data/operatori.csv', index=False)

# 4. GENERAZIONE RICHIESTE (Fatto Generatore con trend temporali e logica coerente)
print("Generazione tabella Richieste...")
richieste_id = [f"REQ_{str(i).zfill(5)}" for i in range(1, NUM_RICHIESTE + 1)]

# Generiamo date coerenti lungo il 2025/2026
date_richieste = []
base_date = datetime(2025, 6, 1)
for _ in range(NUM_RICHIESTE):
    # Aggiungiamo giorni casuali
    giorni_aggiuntivi = np.random.randint(0, 300)
    # Generiamo un'ora con una distribuzione realistica (picchi a mezzogiorno e di sera)
    ore_casuali = int(np.random.choice(
        [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 1, 2, 3, 4, 5, 6, 7],
        p=[0.05, 0.05, 0.08, 0.08, 0.12, 0.10, 0.06, 0.06, 0.06, 0.08, 0.12, 0.10, 0.02, 0.01, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.01]
    ))
    minuti_casuali = np.random.randint(0, 60)
    data_completa = base_date + timedelta(days=giorni_aggiuntivi, hours=ore_casuali, minutes=minuti_casuali)
    date_richieste.append(data_completa)

# Ordiniamo le date in modo cronologico
date_richieste.sort()

# Composizione finale richieste
richieste_list = []
for i in range(NUM_RICHIESTE):
    stato = np.random.choice(STATI_RICHIESTA)
    
    # Se la richiesta è completata ha senso definire un importo e una durata di erogazione
    if stato == 'Completata':
        importo = round(float(np.random.exponential(scale=45.0) + 15.0), 2)  # Prezzo medio intorno ai 60€
        tempo_erogazione = int(np.random.normal(loc=90, scale=30))  # Media 90 minuti
        tempo_erogazione = max(15, tempo_erogazione)  # Almeno 15 minuti di servizio
    elif stato == 'In Corso':
        importo = round(float(np.random.exponential(scale=40.0) + 15.0), 2)
        tempo_erogazione = np.nan  # Non ancora calcolabile
    else:  # Annullata
        importo = 0.0
        tempo_erogazione = np.nan

    richieste_list.append({
        'richiesta_id': richieste_id[i],
        'cliente_id': np.random.choice(df_clienti['cliente_id']),
        'fornitore_id': np.random.choice(df_fornitori['fornitore_id']),
        'operatore_id': np.random.choice(df_operatori['operatore_id']),
        'data_ora': date_richieste[i].strftime('%Y-%m-%d %H:%M:%S'),
        'importo': importo,
        'tempo_erogazione_minuti': tempo_erogazione,
        'stato': stato
    })

df_richieste = pd.DataFrame(richieste_list)
df_richieste.to_csv('data/richieste.csv', index=False)

print("Tutti i file CSV sono stati generati con successo nella cartella 'data'!")