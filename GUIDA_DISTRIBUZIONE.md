# NextCare - Guida alla Distribuzione su Web Server (Produzione)

Questa guida descrive i passi necessari per ospitare la piattaforma NextCare su un server web reale (Intranet o Cloud), connetterla stabilmente ad un server MySQL di produzione e configurare lo scambio LIS con percorsi di rete UNC (cartelle condivise).

---

## 1. Architettura di Produzione

La piattaforma è composta da:
1.  **Frontend (Client Statico)**: File HTML, CSS e JS (`index.html`, `style.css`, `app.js`) caricati dal browser dell'utente.
2.  **Backend (API Server)**: Script Python (`server.py`) in ascolto sulla porta `8000`. Gestisce le email, i test di connessione, l'esportazione LIS ed il parsing dei risultati XML.
3.  **Database Relazionale**: Server MySQL (porta `3306`) che memorizza tutti i dati dell'applicazione.
4.  **Cartelle di Scambio LIS (Middleware)**: Percorsi di rete UNC (es. `\\server\LIS_Exchange\export` e `import`) accessibili in lettura e scrittura sia dal server Python che dagli strumenti di laboratorio.

```mermaid
graph TD
    User([Browser Utente]) -->|Port 80/443| Proxy[Nginx / IIS Reverse Proxy]
    Proxy -->|File Statici| Static[index.html / css / js]
    Proxy -->|API Requests /api/*| PyServer[Python API Server - Port 8000]
    PyServer -->|Query SQL| MySQL[(MySQL Database - Port 3306)]
    PyServer -->|Lettura/Scrittura XML| LIS[\\server\LIS_Exchange\ - Cartelle UNC]
```

---

## 2. Configurazione Iniziale (Setup Wizard)

NextCare include una procedura guidata simile all'installazione di WordPress. Al primo accesso (o se il database non è configurato):
1.  Viene mostrato automaticamente il **Setup Wizard**.
2.  Inserisci i parametri di connessione di MySQL (Host, Porta, Nome Database, Username, Password).
3.  Inserisci i percorsi di rete per il middleware LIS (supporta percorsi UNC tipo `\\nomeserver\condivisione\cartella`).
4.  Clicca su **"Installa & Inizializza NextCare"**: il backend creerà automaticamente il database, importerà le tabelle da `schema.sql` e popolerà i servizi medici/esami LIS dai semi JSON (`lis_services_seed.json` e `ris_visite_services_seed.json`).

---

## 3. Guida Passaggio per Passaggio alla Distribuzione

### Passo 1: Preparare i File sul Server
Crea una cartella sul server di destinazione (es. `C:\inetpub\wwwroot\NextCare` su Windows o `/var/www/nextcare` su Linux) e copia all'interno i seguenti file:
*   `index.html`, `style.css`, `app.js`
*   `server.py`, `schema.sql`
*   `lis_services_seed.json`, `ris_visite_services_seed.json`

### Passo 2: Configurare le Cartelle di Scambio LIS (UNC)
Per far comunicare il middleware LIS (es. SynlabNET) con NextCare:
1.  Sul server o su un NAS, crea una cartella principale (es: `NextCare_LIS_Exchange`) con all'interno due cartelle: `export` e `import`.
2.  Condividi in rete la cartella garantendo i **permessi di lettura/scrittura** (sia a livello di condivisione di rete che di sicurezza NTFS) all'utente che esegue il server Python e alle macchine del laboratorio.
3.  Nel pannello Database di NextCare, configura i percorsi come UNC, ad esempio:
    *   **Export:** `\\192.168.1.100\NextCare_LIS_Exchange\export`
    *   **Import:** `\\192.168.1.100\NextCare_LIS_Exchange\import`

---

### Passo 3: Configurare Python come Servizio di Rete

Per far sì che `server.py` rimanga costantemente attivo in background ed all'avvio del sistema:

#### Opzione A: Distribuzione su Windows (NSSM)
1.  Scarica **NSSM (Non-Sucking Service Manager)**.
2.  Apri il prompt dei comandi come Amministratore ed esegui:
    ```cmd
    nssm.exe install NextCareService
    ```
3.  Nella GUI di configurazione:
    *   **Path**: Seleziona il percorso del tuo eseguibile python (es. `C:\Python312\python.exe`).
    *   **Startup directory**: La cartella dell'applicazione (es. `C:\inetpub\wwwroot\NextCare`).
    *   **Arguments**: `server.py`
4.  Clicca su *Install Service* e avvialo da `services.msc`.

#### Opzione B: Distribuzione su Linux (systemd)
1.  Crea un file di servizio:
    ```bash
    sudo nano /etc/systemd/system/nextcare.service
    ```
2.  Aggiungi la configurazione:
    ```ini
    [Unit]
    Description=NextCare Python Backend Service
    After=network.target

    [Service]
    Type=simple
    User=www-data
    WorkingDirectory=/var/www/nextcare
    ExecStart=/usr/bin/python3 server.py
    Restart=always

    [Install]
    WantedBy=multi-user.target
    ```
3.  Abilita e avvia il servizio:
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl enable nextcare
    sudo systemctl start nextcare
    ```

---

### Passo 4: Configurare il Reverse Proxy (Nginx o IIS)

Si raccomanda di utilizzare un Reverse Proxy davanti all'applicazione per servire in modo efficiente i file statici e proteggere l'API.

#### Configurazione Nginx (Linux)
Crea una configurazione in `/etc/nginx/sites-available/nextcare` e abilitala:
```nginx
server {
    listen 80;
    server_name medical.nextcare.lan; # o l'IP del server

    # Cartella dei file statici di NextCare
    root /var/www/nextcare;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }

    # Proxy delle richieste API verso il server Python (Porta 8000)
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Disabilita il caching per le API
        add_header Cache-Control "no-store, no-cache, must-revalidate";
    }
}
```

#### Configurazione IIS (Windows)
1.  Installa il modulo **URL Rewrite** e **Application Request Routing (ARR)** su IIS.
2.  Crea un nuovo sito Web che punta alla cartella `C:\inetpub\wwwroot\NextCare`.
3.  Nel file `web.config`, definisci una regola di riscrittura che reindirizza le chiamate `/api/*` a `http://localhost:8000/api/{R:1}`.
