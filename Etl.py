import pandas as pd
import sqlite3
import os

# Definiamo i percorsi dei file
CSV_CLIENTI = 'data/clienti.csv'
CSV_FORNITORI = 'data/fornitori.csv'
CSV_OPERATORI = 'data/operatori.csv'
CSV_RICHIESTE = 'data/richieste.csv'
DB_PATH = 'data_warehouse.db'

def run_etl():   
    # 1. ESTRAZIONE (Extraction)
    print("Estrazione dati dai file CSV...")
    if not all(os.path.exists(f) for f in [CSV_CLIENTI, CSV_FORNITORI, CSV_OPERATORI, CSV_RICHIESTE]):
        raise FileNotFoundError("Uno o più file CSV mancano nella cartella 'data'. Esegui prima il generatore di dati!")
        
    df_cli = pd.read_csv(CSV_CLIENTI)
    df_for = pd.read_csv(CSV_FORNITORI)
    df_ope = pd.read_csv(CSV_OPERATORI)
    df_req = pd.read_csv(CSV_RICHIESTE)

    # 2. TRASFORMAZIONE (Transformation)
    # Pulizia valori nulli e standardizzazioni base
    # Nel DWH, gestiamo i valori mancanti delle richieste non completate impostando valori di default o lasciandoli coerenti
    df_req['importo'] = df_req['importo'].fillna(0.0)
    df_req['tempo_erogazione_minuti'] = df_req['tempo_erogazione_minuti'].fillna(-1) # -1 indica "non applicabile/in corso/annullata"

    # Creazione della dimensione TEMPO (dim_tempo) a partire dalle date delle richieste
    df_req['datetime_parsed'] = pd.to_datetime(df_req['data_ora'])
    
    # Estraiamo i dettagli temporali unici presenti nelle richieste
    id_tempo_ser = df_req['datetime_parsed'].dt.strftime('%Y%m%d%H') # Chiave surrogate basata sull'ora (YYYYMMDDHH)
    
    # Costruiamo il DataFrame dim_tempo
    dim_tempo = pd.DataFrame({
        'tempo_id': id_tempo_ser,
        'data_ora': df_req['data_ora'],
        'anno': df_req['datetime_parsed'].dt.year,
        'mese': df_req['datetime_parsed'].dt.month,
        'giorno': df_req['datetime_parsed'].dt.day,
        'ora': df_req['datetime_parsed'].dt.hour,
        'giorno_settimana': df_req['datetime_parsed'].dt.day_name() 
    }).drop_duplicates(subset=['tempo_id']) # Evitiamo duplicati sulla chiave primaria temporale
    
    # Colleghiamo la tabella delle richieste (fatti) alla dimensione tempo tramite la chiave esterna tempo_id
    df_req['tempo_id'] = id_tempo_ser
    
    # Selezioniamo e riordiniamo le colonne per la Fact Table delle Richieste
    fact_richieste = df_req[[
        'richiesta_id', 'cliente_id', 'fornitore_id', 'operatore_id', 
        'tempo_id', 'importo', 'tempo_erogazione_minuti', 'stato'
    ]]

    # 3. CARICAMENTO (Loading)
    print(f"Connessione al database SQLite '{DB_PATH}'...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Abilitiamo le chiavi esterne su SQLite
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Reset delle tabelle se esistono già (per garantire la riproducibilità)
    cursor.execute("DROP TABLE IF EXISTS fact_richieste;")
    cursor.execute("DROP TABLE IF EXISTS dim_clienti;")
    cursor.execute("DROP TABLE IF EXISTS dim_fornitori;")
    cursor.execute("DROP TABLE IF EXISTS dim_operatori;")
    cursor.execute("DROP TABLE IF EXISTS dim_tempo;")


    # Tabelle delle Dimensioni
    cursor.execute("""
    CREATE TABLE dim_clienti (
        cliente_id TEXT PRIMARY KEY,
        zona TEXT,
        data_iscrizione TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE dim_fornitori (
        fornitore_id TEXT PRIMARY KEY,
        nome TEXT,
        categoria_servizio TEXT,
        zona_operativa TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE dim_operatori (
        operatore_id TEXT PRIMARY KEY,
        zona_competenza TEXT,
        tipo_attivita TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE dim_tempo (
        tempo_id TEXT PRIMARY KEY,
        data_ora TEXT,
        anno INTEGER,
        mese INTEGER,
        giorno INTEGER,
        ora INTEGER,
        giorno_settimana TEXT
    );
    """)

    # Tabella dei Fatti (con Vincoli di Integrità Referenziale)
    cursor.execute("""
    CREATE TABLE fact_richieste (
        richiesta_id TEXT PRIMARY KEY,
        cliente_id TEXT,
        fornitore_id TEXT,
        operatore_id TEXT,
        tempo_id TEXT,
        importo REAL,
        tempo_erogazione_minuti INTEGER,
        stato TEXT,
        FOREIGN KEY (cliente_id) REFERENCES dim_clienti(cliente_id),
        FOREIGN KEY (fornitore_id) REFERENCES dim_fornitori(fornitore_id),
        FOREIGN KEY (operatore_id) REFERENCES dim_operatori(operatore_id),
        FOREIGN KEY (tempo_id) REFERENCES dim_tempo(tempo_id)
    );
    """)
    conn.commit()

    # Scrittura dei dati trasformati nei rispettivi oggetti SQL
    print("Scrittura dei record nel database...")
    df_cli.to_sql('dim_clienti', conn, if_exists='append', index=False)
    df_for.to_sql('dim_fornitori', conn, if_exists='append', index=False)
    df_ope.to_sql('dim_operatori', conn, if_exists='append', index=False)
    dim_tempo.to_sql('dim_tempo', conn, if_exists='append', index=False)
    fact_richieste.to_sql('fact_richieste', conn, if_exists='append', index=False)

    print("Verifica rapida del caricamento...")
    count_richieste = cursor.execute("SELECT COUNT(*) FROM fact_richieste;").fetchone()[0]
    print(f"-> Righe caricate con successo in 'fact_richieste': {count_richieste}")

    conn.close()
    print("--- Processo ETL Completato con Successo! ---")

if __name__ == '__main__':
    run_etl()

