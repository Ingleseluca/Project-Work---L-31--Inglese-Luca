import sqlite3
import pandas as pd

# IMPORTANTE: Inserisci qui il percorso assoluto del tuo file .db
# Esempio: r'C:\Users\Utente\project_work\data\data_warehouse.db'
DB_PATH = r'"C:\Users\lucai\OneDrive\Desktop\Startup_onDemand_PW\data_warehouse.db"'

# Connessione al database
conn = sqlite3.connect(DB_PATH)

# 1. Caricamento delle 4 Viste dei KPI (tabelle separate)
kpi_totale_richieste = pd.read_sql_query("SELECT * FROM view_kpi_totale_richieste", conn)
kpi_incasso_totale = pd.read_sql_query("SELECT * FROM view_kpi_incasso_totale", conn)
kpi_tempo_medio = pd.read_sql_query("SELECT * FROM view_kpi_tempo_medio", conn)
kpi_fidelizzazione = pd.read_sql_query("SELECT * FROM view_kpi_fidelizzazione", conn)

# 2. Caricamento dello schema a stella fisico (tabelle separate per i grafici)
fact_richieste = pd.read_sql_query("SELECT * FROM fact_richieste", conn)
dim_clienti = pd.read_sql_query("SELECT * FROM dim_clienti", conn)
dim_fornitori = pd.read_sql_query("SELECT * FROM dim_fornitori", conn)
dim_operatori = pd.read_sql_query("SELECT * FROM dim_operatori", conn)
dim_tempo = pd.read_sql_query("SELECT * FROM dim_tempo", conn)

# Chiudiamo la connessione
conn.close()