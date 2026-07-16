# Project-Work---L-31--Inglese-Luca
# 📊 Data Warehouse & Business Intelligence: Project Work
### Monitoraggio Operativo dei KPI di Servizio (Ticket e Commesse)
**Sviluppato da:** Luca Inglese 

---

## 📂 Struttura del Progetto

La cartella di lavoro contiene i seguenti file e script organizzati per gestire l'intero ciclo di vita del dato (dalla generazione sintetica alla dashboard finale):

```text
├── data/                         # Cartella per l'archiviazione di dati grezzi o temporanei
├── analytics_queries.py          # Script SQL/Python per la creazione e la verifica delle Viste KPI
├── Dashboard_Luca_Inglese.pbix   # Report interattivo sviluppato in Power BI Desktop
├── data_warehouse.db             # Database relazionale locale SQLite (il nostro Data Warehouse)
├── etl.py                        # Pipeline ETL (Extract, Transform, Load) per la modellazione dei dati
├── generator.py                  # Generatore di dati simulati (Clienti, Operatori, Richieste, ecc.)
└── requirements.txt              # Elenco delle dipendenze Python necessarie per riprodurre il progetto
---

## 🛠️ Architettura Tecnica e Scelte Metodologiche

### 1. Schema a Stella (Star Schema)
Il Data Warehouse è modellato seguendo i principi di dimensionalità per garantire massime prestazioni di query ed estrema facilità di utilizzo in Power BI:
*   **Tabella dei Fatti (`fact_richieste`)**: Contiene le misure quantitative transazionali (minuti di erogazione, importo fatturato) e le chiavi esterne.
*   **Tabelle Dimensionali**: 
    *   `dim_clienti`: Anagrafica dei clienti con area geografica e livello di tiering.
    *   `dim_operatori`: Staff tecnico interno suddiviso per team di competenza.
    *   `dim_fornitori`: Terze parti di supporto logistico/tecnologico.
    *   `dim_tempo`: Calendario dettagliato per consentire analisi temporali dinamiche.

### 2. Spostamento del Calcolo sul Database (Database Pushdown)
Per non appesantire Power BI con formule DAX complesse, tutti i KPI principali sono stati calcolati direttamente a livello di database tramite **Viste (VIEW) SQL**. Power BI si limita a leggere i risultati aggregati, garantendo un caricamento quasi istantaneo del report.

---

## 📈 Viste SQL Separate (KPI)

Nel database sono configurate le seguenti viste analitiche, caricate come tabelle separate nel report:

1.  **`view_kpi_totale_richieste`**: Calcola il volume complessivo dei ticket gestiti.
2.  **`view_kpi_incasso_totale`**: Calcola i ricavi totali generati esclusivamente dalle commesse completate con successo.
3.  **`view_kpi_tempo_medio`**: Calcola il tempo medio di erogazione (in minuti) escludendo i ticket non completati o con anomalie.
4.  **`view_kpi_fidelizzazione`**: Identifica la percentuale di clienti ricorrenti (più di una richiesta effettuata nel tempo).

---

## 🚀 Come Riprodurre il Progetto

### Requisiti Preliminari
*   **Python 3.x**
*   Libreria **Pandas** (`pip install pandas`)
*   **Power BI Desktop** (per la visualizzazione della dashboard)

### Istruzioni per l'Esecuzione

1.  **Inizializza il Database e popola le Tabelle Fisiche:**
    Esegui lo script ETL per creare il file del database e generare i dati di test.
    ```bash
    python src/etl_popolamento.py
    ```

2.  **Genera le Viste SQL dei KPI:**
    Esegui lo script per configurare le viste analitiche separate all'interno di SQLite.
    ```bash
    python src/crea_viste_separate.py
    ```

3.  **Carica i dati in Power BI:**
    *   Apri Power BI Desktop.
    *   Seleziona **Recupera dati** > **Altro...** > **Script Python**.
    *   Incolla il codice presente in `script_caricamento_pbi.py` (assicurati di aggiornare il percorso assoluto alla cartella del database `.db`).
    *   Seleziona tutte le tabelle (`fact`, `dim` e le 4 viste `kpi`) e clicca su **Carica**.

4.  **Collega le relazioni a stella:**
    Nel pannello relazioni di Power BI, connetti le tabelle dimensionali alla tabella dei fatti `fact_richieste` tramite i rispettivi ID (relazioni 1-a-molti). Le tabelle KPI restano isolate per popolare le singole Schede visive.

---

## 🔮 Sviluppi Futuri e Miglioramenti
*   **Integrazione Dati Reali**: Sostituzione dello script di simulazione con un connettore diretto (API o ODBC) verso database transazionali reali.
*   **Gestione Storico (SCD Tipo 2)**: Tracciamento delle modifiche anagrafiche per non falsare le analisi temporali passate in caso di aggiornamenti (es. cambio di reparto di un operatore).
*   **Aggiornamento Incrementale**: Configurazione del refresh incrementale in Power BI per caricare solo i nuovi dati giornalieri.
*   **Pipeline di Data Quality**: Implementazione di script di test per bloccare in ingresso record anomali o corrotti (es. importi negativi).
