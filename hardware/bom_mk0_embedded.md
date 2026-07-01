# Bill of Materials (BOM) - Architettura MK0 Embedded

Questa è una versione della BOM dedicata esclusivamente alla **Proposta Tecnica MK0**, l'architettura minimale progettata per essere un prototipo operativo robusto e deterministico, indipendente dal carico cognitivo di ROS 2 e Jetson (riservati all'architettura Mulo X-1). 

I componenti sono stati estratti dal documento di studio dell'architettura MK0 (Follow-me UWB).

## 1. Logica di Controllo e Safety
- **Microcontrollore Principale:** Modulo **ESP32-S3** (si occupa della state machine, logging, e interfacciamento bus CAN). Sostituisce la complessità di Linux/Jetson.
- **Transceiver di rete:** Modulo CAN Bus Transceiver (es. TJA1050 / SN65HVD230) per la comunicazione con i driver motori VESC.
- **Memoria di Logging:** Modulo lettore Micro-SD (interfaccia SPI) per il log diagnostico CSV/JSONL di telemetria e fault.

## 2. Sensori di Navigazione e Follow-Me
In questa architettura si escludono LiDAR complessi e telecamere (YOLO), a favore di sensori deterministici:
- **Inseguimento (Follow-Me):** **3x Moduli UWB** (Ultra-Wideband). Due montati frontalmente sul rover (Anchor) ad una distanza fissa, e uno indossato dall'operatore (Tag).
- **Rilevamento Ostacoli Frontali:** **4x Sensori ToF (Time-of-Flight)** (es. ST VL53L5CX / VL53L1X). Due montati in basso (per ostacoli e vuoti) e due in alto.
- **Stima Assetto (Safety):** **IMU BNO085 o BNO086** (per limitare pendenza, vibrazioni eccessive o tagliare trazione prima del ribaltamento).
- **Tracciamento Globale:** Modulo **GNSS / GPS** (es. u-blox). Usato **solo** per logging e geofence, NON nel loop di controllo del follow-me.

## 3. Alimentazione e Architettura di Ricarica (Range Extender)
Questa versione è pesantemente focalizzata sulla sopravvivenza in outdoor e l'autosufficienza energetica:
- **Batteria Primaria:** Pacco LiFePO4 24V (25.6V effettivi, 100Ah).
- **Caricabatterie di Bordo (AC-DC):** **Mean Well NPB-750**. Garantisce ricarica rapida fino a 22.5A.
- **Caricatore Solare (DC-DC):** Regolatore **Victron SmartSolar MPPT** (con protocollo seriale VE.Direct).
- **Pannello Solare:** Kit pieghevole portatile da **200W** (connessioni MC4 per le soste).
- **Generatore Tampone:** Gruppo elettrogeno a benzina da **1000W / 1200W** (sistema ibrido serie).
- **Componenti Elettrici di Raccordo:**
  - **Diodi Ideali:** Moduli per parallelizzare l'uscita del caricatore Mean Well e del Victron senza reflussi di corrente verso il bus batteria.
  - **Sensore di Corrente:** Sensore a effetto Hall **ACS758** collegato all'ESP32 per leggere il prelievo dal generatore.
  - **Isolamento Dati:** Fotoaccoppiatore Veloce **6N137** per leggere in totale isolamento galvanico i dati VE.Direct dal Victron MPPT all'ESP32-S3.

## 4. Drivetrain e Potenza
*(Identico alla Baseline Meccanica)*
- **Driver Motori:** 4x o 2x Controller compatibili VESC gestiti via CAN Bus.
- **Motori:** 4x Motoriduttori Stepperonline 24V 200W o Hub Motor E-bike.
- **E-Stop Hardware:** Pulsante a fungo fisico NC e contattori per scollegare fisicamente la trazione in emergenza.
