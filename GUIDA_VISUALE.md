# NextCare - Guida Visuale all'Installazione e Distribuzione

Questa guida illustra visivamente i passaggi chiave per il caricamento, la configurazione iniziale ed il funzionamento dell'architettura di rete di NextCare.

---

## 1. Schema Architetturale di Produzione

Il diagramma seguente mostra come i client (browser di medici e operatori) comunicano con il Web Server locale (tramite Reverse Proxy), il quale si collega a MySQL e dialoga con il middleware LIS leggendo e scrivendo nelle cartelle condivise di rete (percorsi UNC).

![Schema di Rete e Flusso Dati LIS](file:///C:/Users/robpiron/.gemini/antigravity/brain/4e261f84-2c21-4fbb-8677-a352af49bbdc/nextcare_architecture_diagram_1781213160418.png)

---

## 2. Configurazione Iniziale (Setup Wizard)

Al primo accesso alla piattaforma, NextCare carica la procedura d'installazione guidata automatica.

![Interfaccia di Installazione Guidata](file:///C:/Users/robpiron/.gemini/antigravity/brain/4e261f84-2c21-4fbb-8677-a352af49bbdc/nextcare_setup_wizard_1781213144862.png)

### Istruzioni di Inizializzazione:
1.  **MySQL Host & Porta:** Inserisci l'IP o il nome host del database (es. `localhost` o l'IP locale `192.168.1.5`).
2.  **Credenziali Database:** Inserisci lo username (es: `root`) ed la password del database.
3.  **Nome Database:** Scegli il nome del database (es: `nextcare_db`). Verrà creato automaticamente se non esiste.
4.  **Cartelle XML LIS:**
    *   Imposta i percorsi UNC condivisi in rete locale per dialogare con lo strumento (es: `\\192.168.1.100\LIS_Exchange\export`).
    *   Assicurati che sia il software del laboratorio che il server NextCare abbiano i permessi di lettura/scrittura su questi percorsi.
5.  Premendo **"Installa & Inizializza NextCare"**, lo script:
    *   Inizializza le tabelle del database da `schema.sql`.
    *   Scrive i parametri nel file `config.json` sul server.
    *   Importa in automatico tutte le prestazioni mediche, visite ed esami LIS (con relativi parametri ed unità di misura).
