# Data Warehouse & Business Intelligence: Project Work
### Monitoraggio Operativo dei KPI di Servizio (Ticket e Commesse)
**Sviluppato da:** Luca Inglese

---

## Struttura del progetto

Nella cartella trovate tutto quello che serve a ricostruire il progetto dall'inizio alla fine, dalla generazione dei dati fino alla dashboard finale. La cartella `data/` raccoglie i dati grezzi o temporanei. Lo script `analytics_queries.py` crea e verifica le viste KPI. Il file `Dashboard_Luca_Inglese.pbix` è il report vero e proprio, sviluppato in Power BI. Il database vero e proprio, cioè il Data Warehouse, è il file SQLite `data_warehouse.db`. `etl.py` contiene la pipeline che si occupa della modellazione dei dati, mentre `generator.py` genera i dati simulati (clienti, operatori, richieste e così via). Infine `requirements.txt` elenca le dipendenze Python necessarie per riprodurre tutto.

---

## Come è stato costruito

Ho modellato il Data Warehouse seguendo lo schema a stella, che resta il modo più semplice per avere query veloci e un collegamento pulito con Power BI. Al centro c'è la tabella dei fatti `fact_richieste`, che contiene le misure quantitative come i minuti di erogazione e l'importo fatturato, oltre alle chiavi esterne verso le dimensioni. Intorno a questa tabella ruotano quattro dimensioni: `dim_clienti`, con l'anagrafica dei clienti, l'area geografica e il livello di tiering; `dim_operatori`, con lo staff tecnico interno diviso per team; `dim_fornitori`, per le terze parti che offrono supporto logistico o tecnologico; e `dim_tempo`, il calendario che permette le analisi temporali.

Invece di caricare Power BI di formule DAX complesse, ho preferito spostare il calcolo dei KPI principali direttamente sul database, attraverso delle viste SQL. In questo modo Power BI si limita a leggere i risultati già aggregati, e il report si carica quasi all'istante.

---

## Le viste KPI

Sono quattro in totale, ognuna caricata come tabella a sé nel report. `view_kpi_totale_richieste` calcola il volume complessivo dei ticket gestiti. `view_kpi_incasso_totale` calcola i ricavi generati esclusivamente dalle commesse concluse con successo. `view_kpi_tempo_medio` calcola il tempo medio di erogazione in minuti, escludendo i ticket incompleti o con anomalie. `view_kpi_fidelizzazione`, infine, individua la percentuale di clienti che hanno effettuato più di una richiesta nel tempo.

---

## Come riprodurlo

Per riprodurre il progetto serve Python 3.x, la libreria Pandas (installabile con `pip install pandas`) e Power BI Desktop per visualizzare la dashboard.

Il primo passo è inizializzare il database e popolare le tabelle, lanciando `etl_popolamento.py`. Fatto questo, si generano le viste SQL dei KPI eseguendo `crea_viste_separate.py`, che configura le viste analitiche dentro SQLite. A questo punto si può passare a Power BI Desktop: da lì si va su Recupera dati, poi Altro, poi Script Python, e si incolla il codice presente in `script_caricamento_pbi.py`, avendo cura di aggiornare il percorso assoluto verso il file `.db`. Si selezionano tutte le tabelle, quindi `fact`, le `dim` e le quattro viste `kpi`, e si clicca su Carica. L'ultimo passaggio è collegare le relazioni a stella nel pannello relazioni di Power BI, unendo le tabelle dimensionali alla tabella dei fatti `fact_richieste` tramite i rispettivi ID, con relazioni di tipo uno-a-molti. Le tabelle KPI restano invece isolate, dato che servono solo ad alimentare le singole schede visive.

---

## Cosa manca ancora

Ci sono diversi margini di miglioramento per il futuro. Il più immediato sarebbe sostituire i dati simulati con dati reali, collegandosi tramite API o ODBC ai database transazionali veri. Un altro passo utile sarebbe gestire lo storico delle anagrafiche con un approccio SCD di tipo 2, in modo da non falsare le analisi temporali passate quando qualcosa cambia, ad esempio quando un operatore cambia reparto. Sarebbe interessante anche configurare un aggiornamento incrementale in Power BI, così da caricare solo i dati nuovi ogni giorno invece di ricaricare tutto. Infine, andrebbe implementata una vera pipeline di data quality, con controlli che blocchino in ingresso record anomali o corrotti, come importi negativi.
