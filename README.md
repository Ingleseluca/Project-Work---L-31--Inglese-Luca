# Data Warehouse & Business Intelligence: Project Work
### Monitoraggio Operativo dei KPI di Servizio (Ticket e Commesse)
**Sviluppato da:** Luca Inglese

---

## Struttura del progetto

Nella cartella trovate tutto quello che serve a ricostruire il progetto dall'inizio alla fine, dalla generazione dei dati fino alla dashboard finale:

```text
├── data/                         # dati grezzi o temporanei
├── analytics_queries.py          # script per creare e verificare le viste KPI
├── Dashboard_Luca_Inglese.pbix   # report Power BI
├── data_warehouse.db             # database SQLite (il Data Warehouse vero e proprio)
├── etl.py                        # pipeline ETL per la modellazione dei dati
├── generator.py                  # generatore di dati simulati (clienti, operatori, richieste...)
└── requirements.txt              # dipendenze Python per riprodurre il progetto
```

---

## Come è stato costruito

### Schema a stella

Ho modellato il Data Warehouse seguendo lo schema a stella, che resta il modo più semplice per avere query veloci e un collegamento pulito con Power BI:

- **`fact_richieste`** — la tabella dei fatti, con le misure quantitative (minuti di erogazione, importo fatturato) e le chiavi esterne verso le dimensioni.
- **Dimensioni:**
  - `dim_clienti` — anagrafica clienti, area geografica, livello di tiering
  - `dim_operatori` — staff tecnico interno, diviso per team
  - `dim_fornitori` — terze parti per supporto logistico/tecnologico
  - `dim_tempo` — calendario per le analisi temporali

### Calcolo spostato sul database

Invece di caricare Power BI di formule DAX complesse, ho spostato il calcolo dei KPI principali direttamente sul database, tramite viste SQL. In questo modo Power BI legge solo i risultati già aggregati e il report si carica quasi all'istante.

---

## Le viste KPI

Sono quattro, ognuna caricata come tabella a sé nel report:

1. **`view_kpi_totale_richieste`** — volume complessivo dei ticket gestiti
2. **`view_kpi_incasso_totale`** — ricavi generati dalle commesse concluse con successo
3. **`view_kpi_tempo_medio`** — tempo medio di erogazione (minuti), al netto dei ticket incompleti o con anomalie
4. **`view_kpi_fidelizzazione`** — percentuale di clienti che hanno fatto più di una richiesta

---

## Come riprodurlo

**Serve:**
- Python 3.x
- Pandas (`pip install pandas`)
- Power BI Desktop, per vedere la dashboard

**Passaggi:**

1. Inizializza il database e popola le tabelle:
   ```bash
   python src/etl_popolamento.py
   ```

2. Genera le viste SQL dei KPI:
   ```bash
   python src/crea_viste_separate.py
   ```

3. Carica i dati in Power BI:
   - Apri Power BI Desktop
   - Vai su **Recupera dati** > **Altro...** > **Script Python**
   - Incolla il codice di `script_caricamento_pbi.py` (occhio ad aggiornare il percorso assoluto del file `.db`)
   - Seleziona tutte le tabelle (`fact`, `dim` e le 4 viste `kpi`) e clicca su **Carica**

4. Collega le relazioni a stella: nel pannello relazioni di Power BI, collega le dimensioni a `fact_richieste` tramite i rispettivi ID (relazioni 1-a-molti). Le tabelle KPI restano isolate, servono solo ad alimentare le singole schede visive.

---

## Cosa manca ancora / possibili sviluppi

- **Dati reali** al posto di quelli simulati, tramite un connettore diretto (API o ODBC) verso i database transazionali veri
- **Storico delle anagrafiche (SCD Tipo 2)**, per non falsare le analisi passate quando cambia qualcosa (es. un operatore cambia reparto)
- **Refresh incrementale** in Power BI, per caricare solo i dati nuovi ogni giorno
- **Controlli di data quality**, per bloccare in ingresso record anomali (es. importi negativi)
