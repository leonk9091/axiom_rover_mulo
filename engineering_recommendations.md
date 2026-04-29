# Raccomandazioni Ingegneristiche - Rover "Mulo"

Questo documento raccoglie le raccomandazioni tecniche e strategiche formulate dal Capo Ingegnere per migliorare l'affidabilità, la sicurezza e le prestazioni del rover.

---

## 1. Software di Controllo (Winch & Stabilità)

### Criticità Attuale
- La logica anti-ribaltamento è puramente reattiva e basata su soglie fisse.
- Mancanza di considerazione della dinamica del momento ribaltante.
- Assenza di filtraggio dei dati sensoriali, con rischio di falsi positivi/negativi.

### Raccomandazioni
- **Controllo Adattivo:** Implementare un algoritmo che moduli la tensione del verricello in funzione dell'angolo di pitch e della velocità di variazione dello stesso.
- **Filtraggio Dati:** Integrare filtri digitali (es. Kalman Filter o passa-basso) sui dati degli IMU per ridurre il rumore e migliorare la stabilità della stima.
- **Modalità "Safe Winching":** Introdurre uno stato operativo che limiti automaticamente la velocità e la forza di trazione quando il rover si trova su pendenze critiche.

---

## 2. Gestione dell'Alimentazione Ibrida

### Criticità Attuale
- La gestione del generatore a combustione interna (ICE) si basa su soglie di batteria statiche.
- Nessuna previsione del carico futuro, con rischi di spegnimento improvviso sotto sforzo.

### Raccomandazioni
- **Load Balancing Predittivo:** Sviluppare un algoritmo che analizzi il trend di consumo corrente per avviare il generatore *prima* che la batteria scenda sotto la soglia critica.
- **Watchdog Hardware:** Implementare un circuito di monitoraggio indipendente che verifichi lo stato del BMS e del generatore, capace di forzare uno stato sicuro in caso di malfunzionamento software.
- **Gestione Termica:** Monitorare attivamente le temperature di batteria e generatore per derating dinamico della potenza.

---

## 3. Architettura Meccanica e Tolleranze

### Criticità Attuali
- Giunti e alberi personalizzati presentano potenziali punti di concentrazione delle tensioni.
- Rischi di vibrazioni indotte da disallineamenti minori non compensati.

### Raccomandazioni
- **Specifiche di Tolleranza:** Definire rigorosamente le tolleranze geometriche e dimensionali nei disegni tecnici (es. accoppiamenti ISO H7/g6 per alberi e mozzi).
- **Compensazione Errori:** Sostituire giunti rigidi con giunti elastici o cardanici nelle trasmissioni di potenza per assorbire disallineamenti angolari e assiali.
- **Monitoraggio Vibrazioni:** Installare accelerometri vicino ai supporti dei cuscinetti critici per la manutenzione predittiva e il rilevamento precoce di guasti meccanici.

---

## 4. Sicurezza Funzionale (Functional Safety)

### Criticità Attuale
- L'arresto di emergenza e le protezioni dipendono interamente dallo stack software ROS, che può bloccarsi o latere.

### Raccomandazioni
- **E-Stop Hardware Indipendente:** Realizzare un circuito di arresto emergency (categoria PLd/PLe) che interrompa fisicamente l'alimentazione dei motori, bypassando completamente il software.
- **Watchdog Esterno:** Utilizzare un microcontrollore dedicato (es. Arduino/STM32 semplice) che monitori l'"heartbeat" del computer principale; in caso di silenzio, deve attivare l'E-Stop autonomamente.
- **Fail-Safe Defaults:** Configurare i driver dei motori per entrare in modalità "freewheel" o frenatura attiva in caso di perdita del segnale di controllo.

---

## 5. Navigazione e Percezione

### Criticità Attuale
- Dipendenza esclusiva da telecamere (visione monoculare/stereo), vulnerabile a scarsa illuminazione, polvere o nebbia.

### Raccomandazioni
- **Integrazione LiDAR:** Aggiungere un sensore LiDAR 2D o 3D per garantire la mappatura e l'evitamento ostacoli indipendentemente dalle condizioni di luce.
- **Analisi del Terreno:** Sviluppare un modulo software che stimi la cedevolezza del terreno (slip ratio) basandosi sulla differenza tra velocità angolare delle ruote e velocità lineare stimata, per ottimizzare la distribuzione della coppia.
- **Fusione Sensoriale:** Implementare un nodo di sensor fusion (es. `robot_localization`) che integri odometria, IMU, GPS (se disponibile) e dati exteroceptivi per una stima della posa robusta.

---

## Piano d'Azione Prioritario

1.  **Immediato:** Implementazione E-Stop hardware e Watchdog esterno (Sicurezza).
2.  **Breve Termine:** Revisione delle tolleranze meccaniche e introduzione filtri nel controllo del verricello.
3.  **Medio Termine:** Sviluppo algoritmo di gestione energetica predittiva e integrazione LiDAR.
4.  **Lungo Termine:** Ottimizzazione avanzata della navigazione su terreni deformabili.
