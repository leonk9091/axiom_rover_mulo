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
- Dipendenza esclusiva da telecamere, vulnerabile a condizioni di scarsa illuminazione, polvere, nebbia o texture ripetitive.
- Mancanza di adattamento alla cedevolezza del terreno.

### Raccomandazioni Scientifiche
- **LiDAR-Inertial Odometry (LIO):** Adottare framework state-of-the-art come **LIO-SAM** o **FAST-LIO2** per una stima della posa (localizzazione) estremamente precisa e robusta, sfruttando la fusione stretta tra dati LiDAR e IMU.
- **Classificazione del Terreno con Deep Learning:** Integrare reti neurali convoluzionali (CNN) o trasformers per classificare il terreno (sabbia, roccia, erba) da dati visivi o LiDAR, permettendo al controller di adattare i parametri di trazione e sospensione.
- **Riferimento:** Conferenze top di settore come **ICRA** e **IROS**.

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
