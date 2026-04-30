# Raccomandazioni Ingegneristiche Avanzate - Rover "Mulo"

Questo documento raccoglie le raccomandazioni tecniche di alto livello, basate su letteratura scientifica e best practices industriali (IEEE, ICRA, ISO), per elevare l'affidabilità, la sicurezza e le prestazioni del rover a standard professionali e di ricerca avanzata.

---

## 1. Controllo del Verricello: Da PID a Model Predictive Control (MPC)

### Criticità Attuale
- L'uso di controller PID classici non gestisce adeguatamente le non-linearità del sistema (oscillazione del carico, elasticità del cavo).
- Mancanza di vincoli espliciti sulla tensione massima e sulla velocità di variazione.

### Raccomandazioni Scientifiche
- **Non-linear Model Predictive Control (NMPC):** Abbandonare i PID a favore di un controllore predittivo che utilizzi un modello dinamico del sistema (rover + cavo + carico) per ottimizzare la traiettoria futura rispettando i vincoli fisici in tempo reale.
- **Modellazione Eulero-Lagrange:** Utilizzare l'equazione di Eulero-Lagrange per descrivere accuratamente la dinamica del carico oscillante e l'accoppiamento con la dinamica del rover.
- **Riferimento:** *IEEE Transactions on Robotics*, approcci utilizzati in sistemi di sollevamento autonomo e robotica spaziale.

---

## 2. Stabilità e Prevenzione del Ribaltamento: ZMP e Margini Dinamici

### Criticità Attuale
- Il monitoraggio di angoli di rollio e beccheggio è insufficiente per dinamiche rapide o terreni irregolari.
- Assenza di fusione sensoriale avanzata per la stima dello stato.

### Raccomandazioni Scientifiche
- **Zero-Moment Point (ZMP) & Dynamic Stability Margin (DSM):** Calcolare in tempo reale il punto di momento nullo e il margine di stabilità dinamico per prevedere il ribaltamento prima che avvenga, considerando le forze di inerzia.
- **Unscented Kalman Filter (UKF):** Integrare un UKF per fondere dati da IMU, odometria e sensori di forza, ottenendo una stima dello stato (posizione, velocità, orientamento) più robusta al rumore e alle non-linearità rispetto a un EKF classico.
- **Riferimento:** Metodologie adottate da laboratori come JPL (NASA) ed ETH Zurich per rover planetari e robot bipedi.

---

## 3. Gestione Energetica Ibrida: Equivalent Consumption Minimization Strategy (ECMS)

### Criticità Attuale
- La gestione del generatore ICE basata su soglie fisse è inefficiente e non ottimizza il consumo globale.
- Stima dello stato della batteria (SoC/SoH) potenzialmente imprecisa sotto carichi variabili.

### Raccomandazioni Scientifiche
- **Equivalent Consumption Minimization Strategy (ECMS):** Implementare questa strategia di controllo ottimo per determinare istantaneamente lo split di potenza ottimale tra batteria e generatore, minimizzando il consumo equivalente di carburante sull'intero ciclo operativo.
- **Extended Kalman Filter (EKF) per BMS:** Utilizzare un EKF specifico per la stima congiunta di SoC (State of Charge) e SoH (State of Health), adattandosi ai cambiamenti dei parametri interni della batteria dovuti a temperatura e invecchiamento.
- **Riferimento:** Letteratura consolidata su *Energy Management Systems (EMS)* per veicoli ibridi elettrici (HEV).

---

## 4. Percezione e Navigazione: LiDAR-Inertial Odometry (LIO) e Terrain Analysis

### Criticità Attuale
- **Vulnerabilità Sensoriale:** Eccessiva dipendenza da sensori RGB, inefficaci in condizioni di "degraded visual environments" (polvere, fumo, buio).
- **Ipotesi di Terreno Rigido:** Gli algoritmi di pianificazione attuali non considerano la deformabilità o la scivolosità del suolo, portando a fallimenti in contesti off-road.

### Raccomandazioni Scientifiche
- **Framework LIO (Tightly Coupled):** Implementare **FAST-LIO2** o **Faster-LIO**. Questi algoritmi utilizzano una fusione stretta (tightly coupled) che integra le misure IMU direttamente nel processo di "point cloud registration" tramite filtri di Kalman iterativi (iEKF). Risultano significativamente più robusti a movimenti bruschi e vibrazioni rispetto a odometrie puramente geometriche.
- **Analisi Semantica del Terreno (Semantic Mapping):** Utilizzare reti neurali (es. **RangeNet++** per LiDAR o **SegFormer** per visione) per assegnare una classe semantica a ogni punto della mappa. Questo permette di distinguere tra ostacoli "hard" (roccia) e "soft" (erba alta, cespugli), che possono essere attraversati.
- **Traversability Analysis basata su Geometria e Fisica:** Calcolare mappe di "traversabilità" che combinano la pendenza locale (geometria) con la stima della cedevolezza (fisica). L'integrazione di sensori di sforzo sui motori può permettere una stima online del coefficiente di attrito del terreno.
- **Riferimento:** Ricerche dei laboratori di robotica autonoma (ETH Zurich - RSL, MIT - Marine Robotics Group) presentate a **ICRA** e **IROS**.

---

## 5. Sicurezza Funzionale: Architettura Safety-Critical e ISO 13849

### Criticità Attuale
- Assenza di separazione tra dominio di controllo (ROS) e dominio di sicurezza.
- Nessuna certificazione o approccio strutturato alla sicurezza funzionale.

### Raccomandazioni Scientifiche
- **Architettura Separata:** Isolare completamente le funzioni di sicurezza su un hardware dedicato (es. MCU real-time o FPGA) indipendente dal computer principale che esegue ROS.
- **Safe Torque Off (STO):** Implementare circuiti hardware certificati (categoria PLd/PLe secondo ISO 13849-1) per interrompere fisicamente la coppia ai motori in caso di guasto, indipendentemente dallo stato del software.
- **Watchdog e Heartbeat:** Utilizzare protocolli di comunicazione safety-rated e watchdog hardware per monitorare l'integrità del sistema di controllo.
- **Riferimento:** Standard **ISO 13849-1** e **IEC 61508** per la sicurezza funzionale delle macchine.

---

## 6. Digital Twin e Manutenzione Predittiva (Predictive Maintenance)

### Criticità Attuale
- Mancanza di un modello virtuale sincronizzato con lo stato fisico del rover, che limita la capacità di diagnosi e ottimizzazione operativa.
- Manutenzione reattiva (corrective) anziché predittiva, con conseguenti fermi macchina non pianificati e costi operativi elevati.
- Assenza di storico dati strutturato per l'analisi di trending delle prestazioni.

### Raccomandazioni Scientifiche
- **Digital Twin in Tempo Reale:** Implementare un gemello digitale basato su ROS2-Gazebo (o NVIDIA Isaac Sim) che riceva in streaming i dati di telemetria (stato motori, tensioni, correnti, temperature, pose) tramite protocollo MQTT o DDS. Il modello deve includere sia la dinamica del rover che il modello di degrado dei componenti critici (cuscinetti, spazzole motori, cavo del verricello).
- **Remaining Useful Life (RUL) Estimation:** Utilizzare algoritmi di Machine Learning supervisionati (es. **Random Forest**, **Gradient Boosting**, o reti **LSTM**) addestrati su dataset di failure history per stimare la vita residua dei componenti. Integrare tecniche di **Survival Analysis** (Cox Proportional Hazards) per modellare la probabilità di guasto in funzione dello stress operativo accumulato.
- **Physics-Informed Neural Networks (PINNs):** Combinare modelli fisici first-principles (usura adesiva, fatica del cavo) con reti neurali per ottenere predizioni più accurate rispetto ai puri modelli data-driven, specialmente in condizioni di dati scarsi.
- **Digital Thread:** Mantenere una catena digitale continua che colleghi il design CAD, il modello di simulazione, i dati operativi e il manuale di manutenzione, garantendo tracciabilità completa del ciclo di vita.
- **Riferimento:** *IEEE Access* e *Journal of Manufacturing Systems* per framework Industrial IoT (IIoT) e Digital Twin; metodologie **ISO 13374** per condition monitoring e diagnostics.

---

## 7. Thermal Management Avanzato

### Criticità Attuale
- Assenza di un sistema di gestione termica attiva per inverter, motori e pacco batteria.
- Rischio di thermal runaway nelle batterie LiPo/Li-ion sotto carichi elevati o in ambienti caldi.
- Derating non controllato dei componenti elettronici per surriscaldamento, con perdita di prestazioni.

### Raccomandazioni Scientifiche
- **Battery Thermal Management System (BTMS):** Implementare un sistema attivo di raffreddamento a liquido (liquid cooling plate) o a circolazione d'aria forzata con controllo PID della temperatura. Per applicazioni leggere, valutare **Phase Change Materials (PCM)** a contatto con le celle per assorbimento passivo dei picchi termici. Il controllo deve mantenere la temperatura delle celle entro la finestra ottimale (15-35°C) definita da **IEC 62660-1**.
- **Thermal Modeling e State Estimation:** Sviluppare un modello termico elettro-chimico della batteria (coupled thermal-electric model) stimato tramite EKF per predire distribuzione di temperatura e individuare hot-spots prima che raggiungano soglie critiche.
- **Inverter/Motor Cooling Integration:** Progettare un circuito termico integrato che sfrutti lo scambiatore di calore del generatore ICE per raffreddare l'elettronica di potenza (heat sink con heat pipe o loop termico a due fasi). Ottimizzare tramite CFD (Computational Fluid Dynamics) il flusso d'aria all'interno del telaio.
- **Derating Intelligente:** Implementare algoritmi di power derating basati su modello termico in tempo reale: riduzione progressiva della corrente massima erogabile quando la temperatura giunzione dei MOSFET supera soglie predefinite, con recupero automatico al raffreddamento.
- **Riferimento:** Standard **IEC 62660** (batterie Li-ion per trazione), **SAE J2464** (safety testing), letteratura su *Applied Energy* e *Journal of Power Sources*.

---

## 8. Comunicazioni Resilienti e Mesh Networking

### Criticità Attuale
- Dipendenza da un singolo link di comunicazione (Wi-Fi o 4G) vulnerabile a interferenze, ostacoli e limiti di copertura.
- Assenza di protocolli di comunicazione toleranti ai ritardi (delay-tolerant) per operazioni in ambienti degradati o a lunga distanza.
- Perdita di telemetria e comando in caso di failure del link primario.

### Raccomandazioni Scientifiche
- **Delay-Tolerant Networking (DTN):** Implementare uno stack DTN (bundle protocol, RFC 5050) per garantire la consegna di comandi e dati anche in presenza di disconnessioni intermittenti. Fondamentale per operazioni in gallerie, foreste fitte o zone montane.
- **Mesh Networking Auto-Riconfigurante:** Dotare il rover e eventuali uniti ausiliarie (drone, stazioni base portatili) di radio compatibili con protocolli mesh come **IEEE 802.11s** (Wi-Fi mesh) o **Zigbee/Thread** per reti a basso consumo. Implementare algoritmi di **Adaptive Routing** (es. AODV, OLSR) per trovare automaticamente percorsi ottimali multi-hop.
- **Link Redundancy:** Architettura di comunicazione eterogenea con fail-over automatico: radio a lungo raggio (LoRa/ELRS) per comandi di sicurezza a bassa larghezza di banda, 4G/5G per teleoperazione ad alta definizione, e Wi-Fi 6E per aggiornamenti dati e debug in prossimità della base.
- **Quality of Service (QoS) Differenziato:** Classificare il traffico in classi di priorità (comandi di sicurezza > telemetria critica > video > log) con scheduling deterministico sui buffer di trasmissione.
- **Riferimento:** **IEEE 802.11s**, RFC 5050 (DTN Bundle Protocol), ricerche su reti mesh per robotica mobile presentate a **ICRA** e **IROS**.

---

## 9. Human-Robot Interaction (HRI) e Teleoperazione Immersiva

### Criticità Attuale
- Interfaccia operatore rudimentale, con elevato carico cognitivo e scarsa situational awareness.
- Teleoperazione diretta (joystick) che richiede continua attenzione umana, impedendo supervisione multi-rover.
- Assenza di feedback aptico o visivo immersivo per il controllo del verricello.

### Raccomandazioni Scientifiche
- **Shared Autonomy / Supervisory Control:** Implementare una gerarchia di controllo dove l'operatore definisce obiettivi di alto livello (waypoint, quota carico) mentre il rover gestisce autonomamente i loop di controllo basso livello (anti-collisione, stabilizzazione carico). Utilizzare framework di **Mixed-Initiative Control** per bilanciare autonomia e supervisione umana.
- **Virtual Reality (VR) / Augmented Reality (AR) Interface:** Fornire all'operatore una visualizzazione immersiva 3D della scena tramite point cloud LiDAR sovrapposto a feed video (AR) o ambiente virtuale ricostruito (VR). Integrare indicatori di stato rover, mappe di pericolo e preview della traiettoria pianificata.
- **Haptic Feedback per il Verricello:** Collegare il master joystick a un attuatore aptico che riproduca in scala la tensione del cavo, permettendo all'operatore di "sentire" il carico e rilevare anomalie (incaglio, sovraccarico) percepitivamente.
- **Situational Awareness Multimodale:** Combinare display visivi, allarmi uditivi direzionali e feedback tattili (vibrazioni sul controller) per avvisare l'operatore di condizioni critiche senza sovraccaricare visivamente l'attenzione.
- **Riferimento:** Standard **ISO 10218-1/2** per sicurezza robotica collaborativa; linee guida **IEEE 7000-2021** per considerazioni etiche nel design di sistemi autonomi; ricerche su *ACM Transactions on Human-Robot Interaction*.

---

## 10. Cybersecurity per Robotica Autonoma

### Criticità Attuale
- Architettura ROS/ROS2 con comunicazioni in chiaro, vulnerabile a sniffing, spoofing e command injection.
- Assenza di meccanismi di autenticazione e autorizzazione sui nodi e sui topic.
- Firmware degli ESP32 e controllori di potenza potenzialmente aggiornabile senza verifica crittografica.

### Raccomandazioni Scientifiche
- **ROS2 Security (SROS2):** Abilitare SROS2 per cifratura end-to-end, autenticazione e controllo degli accessi su tutti i topic, service e action. Configurare **DDS-Security** con certificati X.509 e plugin **AccessControl** per definire policy granulari (quali nodi possono pubblicare/sottoscrivere quali topic).
- **Secure Boot e Secure Firmware Update (SFU):** Implementare secure boot chain su ESP32 (efuse, verified boot) e sui controllori principali. Distribuire aggiornamenti firmware Over-The-Air (OTA) firmati digitalmente (ECDSA/RSA), con rollback automatico in caso di verifica fallita.
- **Network Segmentation:** Isolare i domini di comunicazione tramite VLAN o reti fisicamente separate: rete safety-critical (freni, STO) isolata dalla rete operativa (ROS2) e dalla rete di manutenzione/diagnostica (Wi-Fi esterno).
- **Anomaly Detection su Bus di Comunicazione:** Implementare monitoraggio continuo del traffico CAN/Ethernet tramite tecniche di **unsupervised learning** (Isolation Forest, autoencoder) per rilevare pattern anomali indicativi di intrusione o malfunzionamento.
- **Riferimento:** **IEC 62443** (security per sistemi di controllo industriale), **NIST SP 800-82** (Guide to Operational Technology Security), **ISO/IEC 27001**.

---

## 11. Software Architecture: Micro-ROS, Containerizzazione e CI/CD

### Criticità Attuale
- Nodi ROS monolitici difficili da testare e distribuire singolarmente.
- Ambiente di sviluppo non riproducibile tra macchine diverse.
- Assenza di pipeline automatizzata per test, build e deployment.

### Raccomandazioni Scientifiche
- **Micro-ROS su Controllori Embedded:** Migrare i task real-time critici (safety watchdog, controllo motore a basso livello) da nodi ROS2 standard a **micro-ROS** eseguiti su MCU (es. ESP32, STM32) con RTOS (FreeRTOS/Zephyr). Questo garantisce determinismo e latenza garantita (<1ms) per i loop di sicurezza, liberando il computer principale dai task hard real-time.
- **Containerizzazione con Docker/Podman:** Impacchettare ogni nodo ROS2 in container separati con immagini basate su ROS2 Humble/Iron. Utilizzare **Docker Compose** o **Kubernetes (K3s)** per l'orchestrazione su edge-computer. I container devono essere **distroless** o basati su immagini minimale (Alpine Linux o Ubuntu minimal) per ridurre la attack surface.
- **CI/CD Pipeline:** Implementare una pipeline CI/CD (GitHub Actions/GitLab CI) che esegua automaticamente:
  - **Build e Static Analysis:** `colcon build`, `ament_cppcheck`, `ament_flake8`, `clang-tidy`, `cppcheck`.
  - **Unit Testing:** Framework `gtest` (C++) e `pytest` (Python) con coverage minima obbligatoria (>80%).
  - **Integration Testing (SIL):** Esecuzione in container con simulatore Gazebo per testare scenari di regressione.
  - **Security Scanning:** Dependency scanning (`snyk`, `dependabot`) e container image scanning (`trivy`).
- **Infrastructure as Code (IaC):** Versionare insieme al codice sorgente i file di configurazione del sistema (`.yaml` di parametri ROS, `docker-compose.yml`, script di deployment) per garantire riproducibilità completa dell'ambiente.
- **Riferimento:** Best practices **ROS2 Design Patterns**, **DevOps per Robotica** (ROS-Industrial), **ISO/IEC 25010** (quality in use).

---

## 12. Simulation-Based Validation: SIL/HIL

### Criticità Attuale
- Testing prevalentemente condotto su hardware fisico, costoso in termini di tempo e risorse.
- Difficoltà nel riprodurre scenari di guasto e condizioni limite in sicurezza.
- Validazione insufficiente degli algoritmi di controllo prima del deployment sul rover.

### Raccomandazioni Scientifiche
- **Software-in-the-Loop (SIL):** Eseguire l'intero stack software ROS2 in simulazione (Gazebo/Ignition o NVIDIA Isaac Sim) con modelli fisici ad alta fedeltà che includano:
  - Dinamica del contatto ruota-terreno (modello **Pacejka** o **Brush Model**).
  - Elasticità del cavo del verricello e dinamica del carico pendente.
  - Deformazione del terreno (terramechanics model di **Bekker/Wong**).
  - Sensori simulati con rumore realistico estratto da dataset reali o modelli stocastici.
- **Hardware-in-the-Loop (HIL):** Collegare l'elettronica di potenza reale (inverter, BMS, controllori motori) a un simulatore real-time (es. **dSPACE**, **Speedgoat**, o soluzione open **OPAL-RT**) che emuli in tempo reale il comportamento dei motori e delle batterie. Questo permette di validare il firmware e la logica di sicurezza senza rischiare danni hardware.
- **Scenario-Based Testing:** Definire una libreria di scenari standardizzati (curve strette, salite ripide, guasto sensore, perdita di comunicazione, sovraccarico verricello) eseguibili automaticamente in CI. Adottare metriche quantitative di performance (tempo di completamento, consumo energetico, deviazione dalla traiettoria, numero di interventi di sicurezza).
- **Riferimento:** Standard **ISO 26262-6** per testing software automotive; **IEEE 1012** per verification e validation; metodologie HIL/SIL consolidate in ambito aerospaziale (DO-178C).

---

## 13. Ottimizzazione Strutturale e Materiali Avanzati

### Criticità Attuale
- Chassis potenzialmente sovradimensionato, con penalità sul peso complessivo e sul consumo energetico.
- Scelta dei materiali basata su criteri empirici piuttosto che su ottimizzazione strutturale sistematica.
- Limitata considerazione della fatica e delle concentrazioni di sforzo in punti critici.

### Raccomandazioni Scientifiche
- **Topology Optimization:** Applicare tecniche di ottimizzazione topologica (es. metodo **SIMP** - Solid Isotropic Material with Penalization, o **TOBS**) al design del chassis e dei componenti portanti per minimizzare il peso rispettando vincoli di rigidezza, resistenza a fatica e fattore di sicurezza. Utilizzare software come **ANSYS, Altair OptiStruct, o open-source Top3d**.
- **Materiali Compositi e Leghe Leggere:** Valutare l'impiego di:
  - **Alluminio 7075-T6** o **6082-T6** per componenti strutturali principali (ottimo rapporto resistenza/peso).
  - **Compositi CFRP (Carbon Fiber Reinforced Polymer)** per pannelli e supporti non strutturali o semi-strutturali (bracci del verricello, cover).
  - **Titanio Grado 5 (Ti-6Al-4V)** per giunzioni, perni e componenti ad alta sollecitazione specifica dove il peso è critico.
- **Generative Design:** Sfruttare algoritmi di **Generative Design** (AI-based) per esplorare spazi di design non convenzionali, producendo geometrie organiche ottimizzate per i carichi specifici del rover, producibili tramite **Additive Manufacturing (AM)** in metallo (DMLS/SLM).
- **Analisi Fatica e Affidabilità:** Eseguire simulazioni FEM con analisi di fatica a durata limitata (stress-life o strain-life approach) per i componenti soggetti a carichi ciclici (sospensioni, supporti motore, tamburo verricello). Verificare secondo **Eurocode 3** o **ASME** dove applicabile.
- **Riferimento:** **ISO 10360** per materiali; letteratura su *Structural and Multidisciplinary Optimization*; standard **ASTM D3039** per testing compositi.

---

## 14. Vibration Monitoring e Controllo NVH (Noise, Vibration, Harshness)

### Criticità Attuale
- Vibrazioni trasmesse dal terreno irregolare e dai motori che possono danneggiare elettronica sensibile, allentare connessioni e ridurre il comfort operativo.
- Assenza di un sistema di monitoraggio vibratorio per la diagnostica preventiva dei componenti meccanici.
- Sensori e telecamere montati rigidamente, esposti a jitter che degrada le prestazioni di percezione.

### Raccomandazioni Scientifiche
- **Condition Monitoring tramite Analisi Vibrazionale:** Installare accelerometri triassali MEMS (es. **ADXL355, BMI088**) su motori, riduttori, cuscinetti del verricello e telaio principale. Implementare analisi nel dominio delle frequenze (FFT, Welch's method) e tecniche di **Envelope Analysis** per individuare early-stage fault su cuscinetti (BPFO, BPFI, BSF, FTF frequencies). Utilizzare **Order Tracking** per analisi in condizioni di regime variabile.
- **Active Vibration Control (AVC):** Per componenti estremamente sensibili (LiDAR, unità inerziale di precisione, telecamere gimbal), implementare sistemi di isolamento attivo basati su **piezoelectric actuators** o **voice coil motors** controllati tramite **FxLMS (Filtered-x Least Mean Squares)** adaptive filter, che cancellano le vibrazioni in tempo reale.
- **Passive Isolation Optimization:** Progettare supporti passivi (elastomeri, wire rope isolators, sandwich viscoelastic) con frequenza di risonanza calcolata per essere almeno una decade sotto la frequenza di disturbo principale. Validare tramite **Modal Analysis** (FEM) e **Operational Deflection Shape (ODS)**.
- **Vibration-Damping Structural Design:** Integrare nel design strutturale elementi dissipativi (es. strati viscoelastici, tuned mass dampers) per smorzare le risonanze identificate durante l'analisi modale. Utilizzare tecniche di **Constrained Layer Damping (CLD)** su pannelli metallici per ridurre il rumore strutturale.
- **Riferimento:** Standard **ISO 10816** (valutazione vibrazioni macchine), **ISO 2631** (vibrazioni whole-body); letteratura su *Mechanical Systems and Signal Processing* per diagnostica avanzata.

---
