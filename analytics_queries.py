import sqlite3
import os

# Usiamo lo stesso percorso definito nel vostro ETL
DB_PATH = 'data/data_warehouse.db'

def esegui_creazione_e_analisi():
    print("--- 1. Connessione al Database e Creazione delle Viste per Power BI ---")
    
    # Connessione al database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Definiamo le query DDL per creare le viste. 
    # Usiamo DROP VIEW prima di CREATE VIEW per assicurarci di aggiornarle se facciamo modifiche.
    viste_kpi = {
        # Vista 1: Numero di richieste
        "view_kpi_totale_richieste": """
            CREATE VIEW view_kpi_totale_richieste AS
            SELECT 
                COUNT(richiesta_id) AS numero_richieste
            FROM
                fact_richieste;
        """,
        
        # Vista 2: Incasso totale
        "view_kpi_incasso_totale": """
            CREATE VIEW view_kpi_incasso_totale AS
            SELECT 
                ROUND(SUM(importo), 2) AS importo_totale
            FROM
                fact_richieste
            WHERE 
                stato = 'Completata';
        """,
        
        # Vista 3: Tempo medio di erogazione
        "view_kpi_tempo_medio": """
            CREATE VIEW view_kpi_tempo_medio AS
            SELECT 
                ROUND(AVG(tempo_erogazione_minuti), 2) AS tempo_medio_erogazione
            FROM
                fact_richieste
            WHERE
                stato = 'Completata'
                AND tempo_erogazione_minuti >= 0;
        """,
        
        # Vista 4: Tasso di fidelizzazione (% clienti di ritorno)
        "view_kpi_fidelizzazione": """
            CREATE VIEW view_kpi_fidelizzazione AS
            WITH conteggio_richieste AS (   
                SELECT 
                    cliente_id, 
                    COUNT(richiesta_id) AS num_richieste
                FROM
                    fact_richieste
                GROUP BY 
                    cliente_id
            )
            SELECT 
               ROUND((SUM(CASE WHEN num_richieste > 1 THEN 1 ELSE 0 END) * 100.0) / COUNT(*), 2) AS percentuale_fidelizzazione
            FROM 
               conteggio_richieste;
        """,

        # Vista Consolidata (La super-vista "All-in-One" consigliata per Power BI)
        "view_kpi_globali": """
            CREATE VIEW view_kpi_globali AS
            SELECT 
                (SELECT COUNT(richiesta_id) FROM fact_richieste) AS numero_richieste,
                (SELECT ROUND(SUM(importo), 2) FROM fact_richieste WHERE stato = 'Completata') AS importo_totale,
                (SELECT ROUND(AVG(tempo_erogazione_minuti), 2) FROM fact_richieste WHERE stato = 'Completata' AND tempo_erogazione_minuti >= 0) AS tempo_medio_erogazione,
                (
                    WITH conteggio_richieste AS (   
                        SELECT cliente_id, COUNT(richiesta_id) AS num_richieste FROM fact_richieste GROUP BY cliente_id
                    )
                    SELECT ROUND((SUM(CASE WHEN num_richieste > 1 THEN 1 ELSE 0 END) * 100.0) / COUNT(*), 2) FROM conteggio_richieste
                ) AS percentuale_fidelizzazione;
        """
    }

    try:
        # Creazione fisica delle viste nel database SQLite
        for nome_vista, query_ddl in viste_kpi.items():
            cursor.execute(f"DROP VIEW IF EXISTS {nome_vista};")
            cursor.execute(query_ddl)
            print(f" ✓ Vista '{nome_vista}' creata/aggiornata.")
        
        conn.commit()
        print("\n--- 2. Verifica dei Dati Tramite Query sulle Viste Appena Create ---")

        # Ora interroghiamo direttamente la vista globale consolidata per verificare i risultati
        query_test = "SELECT numero_richieste, importo_totale, tempo_medio_erogazione, percentuale_fidelizzazione FROM view_kpi_globali;"
        cursor.execute(query_test)
        riga_kpi = cursor.fetchone()

        # Salviamo e formattiamo i dati estratti dalla vista
        totale_richieste = riga_kpi[0] if riga_kpi[0] is not None else 0
        incasso_totale = riga_kpi[1] if riga_kpi[1] is not None else 0.0
        tempo_medio = riga_kpi[2] if riga_kpi[2] is not None else 0.0
        tasso_fidelizzazione = riga_kpi[3] if riga_kpi[3] is not None else 0.0

        # Mostriamo il report di controllo a schermo
        print("\n================ INDICATORI PRINCIPALI (KPI) ================")
        print(f"• Numero totale di richieste (dalla Vista):   {totale_richieste}")
        print(f"• Incassi totali (dalla Vista):               € {incasso_totale:,.2f}")
        print(f"• Tempo medio di erogazione (dalla Vista):   {tempo_medio} minuti")
        print(f"• Tasso di fidelizzazione (dalla Vista):     {tasso_fidelizzazione}%")
        print("=============================================================\n")
        print("Stato database: Le viste sono salvate e pronte per essere caricate su Power BI!")

    except sqlite3.Error as e:
        print(f"⚠️ Errore durante l'esecuzione delle query SQL: {e}")
    
    finally:
        # Chiudiamo sempre la connessione al database
        conn.close()

if __name__ == '__main__':
    esegui_creazione_e_analisi()