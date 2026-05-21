# Modalità Sentinella Notturna / Guardiano del Campo (Night Sentry Mode)
## Proposta Concettuale di Sviluppo Futuro per Axiom Rover "Mulo"

Questo documento descrive la specifica tecnica concettuale per l'implementazione della **Modalità Sentinella Notturna** (o *Guardiano del Campo*). L'obiettivo è trasformare il Mulo in un supervisore attivo per la sicurezza del perimetro di campeggio durante le ore notturne, in grado di rilevare intrusioni di fauna selvatica (cinghiali, lupi, orsi, cani randagi) o estranei, attivando contromisure visive/acustiche dissuasive e notificando silenziosamente i campeggiatori all'interno delle tende.

---

## 1. Analisi di Sicurezza e Filosofia Operativa: "Sentinella Statica"

Una delle prime ipotesi di sviluppo prevedeva il pattugliamento attivo (movimento fisico del rover attorno al campo). Tuttavia, un'analisi ingegneristica e di sicurezza ha evidenziato rischi inaccettabili:

> [!WARNING]
> **Rischio Collisione con Tiranti delle Tende (Guy Wires):**
> I tiranti delle tende da campeggio sono fili sottili (spesso di spessore inferiore a 3 mm), tesi a terra e di colore scuro o semiriflettente. Sensori LiDAR standard, telecamere e sensori ad ultrasuoni falliscono quasi sempre nel rilevarli in modo affidabile, specialmente di notte. Un movimento lineare del rover causerebbe l'aggrovigliamento delle ruote o del verricello nei tiranti, con il rischio di abbattere le tende sulle persone o causare danni meccanici.

### La Soluzione: Sentinella Statica con Rotazione sul Posto (Yaw-Only Tracking)
Per garantire la massima sicurezza e l'assoluta incolumità delle persone, la modalità sentinella è rigorosamente **statica**:
1. **Posizionamento:** Il rover viene parcheggiato in una posizione strategica rialzata o al limite del campo, orientato verso la zona di potenziale avvicinamento degli animali.
2. **Stazionamento Meccanico:** I freni meccanici a disco **Avid BB7 MTN** vengono bloccati tramite la leva a cricchetto di emergenza. Gli stadi di potenza dei VESC vengono disabilitati per azzerare i consumi dei motori e impedire qualsiasi movimento lineare accidentale.
3. **Inseguimento Angolare (Yaw-Tracking):** In caso di rilevamento confermato ai margini del campo visivo, l'ESP32-S3 sblocca temporaneamente i VESC, esegue una rotazione sul posto estremamente lenta e controllata (Skid-steer yaw) per orientare il frontale del rover (dove risiedono i fari principali e i sensori a lungo raggio) verso la minaccia, per poi ribloccarsi immediatamente. La velocità di rotazione angolare è limitata a:
   `ω_max = 5 deg/s` (circa 0.087 rad/s)
   per prevenire qualsiasi urto brusco.

---

## 2. Pipeline di Rilevamento Multimodale (Detection Pipeline)

Per funzionare in assenza totale di luce senza insospettire o spaventare preventivamente la fauna, il sistema utilizza una combinazione di sensori passivi ad infrarossi e sensori geometrici attivi a bassissimo consumo.

```
+-----------------------------------------------------------------------+
|                           AMBIENTE ESTERNO                            |
+-----------------------------------------------------------------------+
        |                                               |
        v (Radiazione IR Passiva)                       v (Riflessione Laser ToF)
+-------------------------------+               +-------------------------------+
| Matrice Termica (MLX90640)    |               | Array Sensori ToF / LiDAR     |
| 32 x 24 Pixel - Risparmio Energetico |        | (Frequenza ridotta a 2 Hz)    |
+-------------------------------+               +-------------------------------+
        |                                               |
        +-----------------------+-----------------------+
                                |
                                v
                +-------------------------------+
                | ESP32-S3 - Algoritmo Fusion   |
                | - Classificazione Termica     |
                | - Sottrazione Sfondo Geomet.  |
                +-------------------------------+
                                |
             +------------------+------------------+
             | (Minaccia Confermata)               | (Nessuna anomalia)
             v                                     v
+-------------------------------+       +-------------------------------+
| Attivazione Deterrenti        |       | Sleep Mode / Basso Consumo    |
| - Strobo LED MOSFET (24V)     |       | - VESC in Idle                |
| - Buzzer Ultrasuoni           |       | - CPU a 80 MHz                |
| - Notifica LoRa Mesh (Pager)  |       +-------------------------------+
+-------------------------------+
```

### A. Sensore Termico Primario: Matrice di Termopile MLX90640
Il sensore principale è una termocamera radiometrica economica **MLX90640** (32x24 pixel, FOV di 55° o 110°), interfacciata via I2C all'ESP32-S3.
*   **Vantaggi:** Rileva la radiazione infrarossa termica (8–14 µm) emessa da corpi caldi (animali e umani) rispetto allo sfondo freddo del terreno montano notturno.
*   **Range Utile:** Rilevamento affidabile di un animale di medie/grandi dimensioni (es. cane, cinghiale) fino a **10–12 metri** in totale oscurità.
*   **Consumo Ridottissimo:** Solo `23 mA a 3.3V` (~76 mW), ideale per il funzionamento continuo a batteria.

### B. Sottrazione Geometrica dello Sfondo via ToF/LiDAR
Per evitare falsi positivi termici (es. sassi caldi che rilasciano calore accumulato di giorno, correnti d'aria calda), l'ESP32-S3 combina la mappa termica con i sensori di distanza geometrici:
1. **Fase di Inizializzazione (Map Lock):** All'attivazione della modalità sentinella, il sistema mappa le distanze degli ostacoli fissi circostanti tramite i sensori ToF di bordo o un LiDAR 2D configurato in modalità economica (basso numero di giri, es. 2 Hz).
2. **Rilevamento Variazione (Delta Lock):** Se un oggetto solido entra nella zona presidiata, si verifica una variazione della distanza registrata (`d_misurata < d_mappa`).
3. **Coincidenza Spazio-Temporale:** La minaccia è confermata solo se l'anomalia geometrica (ToF) e l'anomalia termica (MLX90640) avvengono nello stesso settore angolare nello stesso istante.

### C. Classificazione Termica Edge (TensorFlow Lite Micro)
Sull'ESP32-S3 viene eseguito un modello neurale leggerissimo per l'analisi dei fotogrammi termici 32x24. Il modello calcola il gradiente di temperatura del cluster in movimento:
*   Un cluster biologico ha un nucleo ad alta temperatura (`T_nucleo >= 32 °C`) e bordi sfumati dovuti alla pelliccia.
*   Un sasso o un oggetto inerte ha un gradiente termico omogeneo e statico.

---

## 3. Sottosistema di Dissuasione (Scare & Actuation)

Una volta confermata l'intrusione a una distanza inferiore alla soglia di sicurezza (es. 6 metri), il rover attiva una sequenza graduata di dissuasione per spaventare l'animale senza aggredirlo fisicamente.

### A. Driver MOSFET per Fari LED a 24V con Strobo Rapido
I fari anteriori LED da **20W + 20W (24V)** vengono pilotati tramite un circuito di commutazione a MOSFET di potenza ad alta efficienza.

#### Schema Elettronico di Principio:
```
                                     +24V (Batteria Mulo)
                                       |
                                     [Fari LED 2x20W]
                                       |
                                       +---------+
                                       |         |
                                      [D1]     [MOSFET]
                                   (1N4007)  (IRLB3034)
                                       |    G    | D
                       [R1] 220 Ohm    +---[ ]---+
                            +---+           | S
 ESP32 GPIO (PWM) --------->|   |-----------+
                            +---+           |
                                           GND
```
*   **Dissuasione Visiva:** Il MOSFET consente di modulare la luminosità tramite PWM. La strategia iniziale prevede l'effetto **Strobo Strobo-Frequenza** (lampeggi rapidi a 8–10 Hz con il 100% di intensità per 3 secondi), altamente disturbante per la vista notturna adattata al buio degli animali selvatici, provocando l'immediata fuga.
*   **Inseguimento Luminoso:** Se l'animale non scappa ma si sposta lateralmente, il rover esegue il tracking angolare (Yaw) mantenendo il cono di luce proiettato direttamente sul bersaglio.

### B. Deterrente Acustico Ultrasonico / Multifrequenza
Accanto ai fari, viene integrato un trasduttore piezoelettrico ad alta direzionalità guidato da un driver a ponte intero (H-Bridge) gestito dall'ESP32-S3.
*   **Frequenze Selettive:** Il sistema genera sweep di frequenza compresi tra **18 kHz e 24 kHz** (ultrasuoni superiori alla soglia uditiva della maggior parte degli umani adulti, ma estremamente fastidiosi per canidi, felidi e ungulati).
*   **Basso Disturbo per l'Uomo:** Consente di spaventare l'animale senza svegliare bruscamente le persone nella tenda con sirene udibili, a meno che la minaccia non persista a distanze critiche (sotto i 3 metri, in cui si attiva anche un segnalatore acustico a 2 kHz udibile come allarme generale).

---

## 4. Sottosistema di Allerta Silenziosa (Wireless Alerting)

La sentinella non deve limitarsi a spaventare l'animale; deve informare i campeggiatori del perimetro violato in modo discreto e tempestivo.

```
+---------------------------+             LoRa Link (868 MHz)              +---------------------------+
|    AXIOM ROVER "MULO"     | ==========================================>  |       PAGER DA TENDA      |
|  Sentinella Notturna      |          Crittografia AES-128                |  (ESP32-C3 + Display OLED)|
+---------------------------+                                              +---------------------------+
                                                                                         |
                                                                                         +---> Vibrazione
                                                                                         +---> Distanza / Azimut
                                                                                         +---> Stato Batteria Rover
```

1. **Il Pager da Tenda (Hardware dedicato):** Un piccolo dispositivo compatto (delle dimensioni di un portachiavi) basato su ESP32-C3, un display OLED da 0.96" e un modulo LoRa **SX1276** a 868 MHz. Viene posizionato all'interno della tenda o tenuto al polso dal campeggiatore.
2. **Protocollo LoRa Mesh / Point-to-Point:** Il Mulo invia pacchetti cifrati AES-128 a bassissima potenza contenenti:
   *   **Stato di Allerta:** Livello di minaccia (Verde = Ok, Giallo = Movimento sospetto, Rosso = Intrusione / Strobo attivo).
   *   **Posizione Relativa:** Angolo (Azimut) della minaccia (es. "Nord-Ovest, 5.4 metri").
   *   **Diagnostica:** Livello di carica residua della batteria del rover.
3. **Notifica Silenziosa:** Il pager avvisa l'operatore tramite un motore a micro-vibrazione interno, consentendo un risveglio controllato e privo di panico, offrendo il tempo di ispezionare l'esterno in sicurezza.

---

## 5. Autonomia ed Energy Budget Notturno (Eco-Sentry Mode)

Un requisito fondamentale è che la modalità sentinella non consumi l'energia preziosa destinata alla trazione del giorno successivo.

### Analisi dei Consumi in Stato di Presidio (10 Ore di Sonno)

| Componente | Tensione | Corrente Nominale | Potenza Assorbita | Stato Operativo |
| :--- | :--- | :--- | :--- | :--- |
| **ESP32-S3 (Microcontrollore)** | 3.3 V | 30 mA | 0.099 W | Clock ridotto a 80 MHz, cores attivi per fusion. |
| **Transceiver LoRa SX1276** | 3.3 V | 15 mA (Rx) | 0.049 W | In ascolto/beaconing periodico a bassissimo duty-cycle. |
| **Sensore Termico MLX90640** | 3.3 V | 23 mA | 0.076 W | Attivo in polling continuo a 4 Hz. |
| **Sensori ToF VL53L1X (x4)** | 2.8 V | 20 mA (Tot) | 0.056 W | Interrogati in modalità sequenziale lenta. |
| **Sensore di Corrente / IMU** | 3.3 V | 10 mA | 0.033 W | Attivi per monitoraggio inclinazione/salute. |
| **Elettronica di potenza VESC (x4)**| 24 V | 0 mA | 0.000 W | **Disabilitati via Gate Driver (Shutdown fisco)**. |
| **DC-DC Step-Down (Perdite)** | - | - | 0.200 W | Efficienza ~85% sui carichi leggeri. |
| **TOTALE PRESIDIO STATICO** | - | - | **~0.513 W** | **Consumo estremamente trascurabile.** |

### Consumo Totale Energia in Presidio Continuo:
`Energia = 0.513 W * 10 h = 5.13 Wh`

Rispetto alla batteria del **Mulo MK0 (24V 100Ah = 2560 Wh)**:
`Frazione Batteria Consumata = (5.13 Wh / 2560 Wh) * 100 = 0.20%`
Il consumo in stato di monitoraggio statico è **praticamente nullo** (pari all'autoscarica naturale della chimica LiFePO4).

### Analisi dei Consumi in Stato di Allarme Attivo (Strobo + Ultrasuoni)

*   **Fari LED (Attivi al 50% duty-cycle strobo):** `20 W` (due fari da 20W modulati al 50% di tempo di accensione).
*   **Piezo Ultrasuoni:** `5 W` ad alta potenza.
*   **Modulo LoRa (Trasmissione Tx a +20 dBm):** `0.396 W` (120 mA a 3.3V).
*   **Rotazione Motori (Opzionale - Yaw lento 5s per tracking):** `45 W` (durante il riallineamento).
*   **Consumo Picco Allarme:** `~70.5 W`

Anche ipotizzando **20 allarmi completi durante la notte** della durata di 1 minuto ciascuno (totale 20 minuti di allarme visivo e tracking attivo):
`Energia Allarmi = 70.5 W * (20 / 60) h = 23.5 Wh`
`Energia Totale Notte (Presidio + Allarmi) = 5.13 Wh + 23.5 Wh = 28.63 Wh`

**Impatto finale sulla batteria del rover:**
`Frazione Consumata = (28.63 Wh / 2560 Wh) * 100 = 1.11%`
Questo assicura che l'autonomia di viaggio diurna del giorno successivo rimanga del tutto inalterata.

---

## 6. Piano di Sviluppo e Integrazione Firmware (Roadmap R&D)

1. **Fase 1 (Prototipazione Termica su ESP32-S3):**
   * Collegamento della matrice MLX90640 su bus I2C.
   * Scrittura dell'algoritmo di estrazione cluster caldi e calcolo baricentro termico su ESP32-S3.
2. **Fase 2 (Integrazione LoRa Mesh):**
   * Configurazione del protocollo di comunicazione bidirezionale a pacchetti ridotti tra Mulo ed ESP32-C3 Pager.
   * Ottimizzazione del Deep Sleep del pager per garantire autonomia di più notti con una mini cella LiPo da 300 mAh.
3. **Fase 3 (Sviluppo Scheda Driver Driver Fari/Piezo):**
   * Sbroglio e prototipazione di una mini shield di potenza isolata per gestire il PWM dei fari da 24V ed il segnale del trasduttore ultrasonico.
4. **Fase 4 (Integrazione di Sicurezza nel Watchdog ROS 2/STM32):**
   * Blocco software ed hardware della trazione lineare durante lo stato `SENTINEL_ACTIVE`.
   * Limitazione rigorosa della coppia di yaw per evitare il ribaltamento o il trascinamento di rami e sassi in caso di fango o pendenze durante il tracciamento angolare.
