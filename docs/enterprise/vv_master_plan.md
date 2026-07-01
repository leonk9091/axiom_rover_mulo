# Verification and Validation Master Plan - Mulo

## Test Livelli

| Livello | Scopo | Ambiente | Gate |
| :--- | :--- | :--- | :--- |
| Unit | Logica pura Python/C++ | CI locale/GitHub | Tutti i test verdi. |
| Integration | ROS graph, topic e launch | Container ROS 2 | Bringup installabile e nodi critici vivi. |
| SIL | Digital twin e fault injection | ROS-Gz/Gazebo | Scenari P0 ripetibili. |
| HIL | MCU/VESC/sensori reali su banco | Ruote sollevate | Stop e fault entro limiti. |
| Bench | Potenza bassa e carico controllato | Banco elettrico/meccanico | Nessun fault non spiegato. |
| Field | Outdoor progressivo | Piano, ghiaia, salita, discesa | Log completo e checklist pre/post. |

## Test P0

| ID | Nome | Metodo | Pass/fail |
| :--- | :--- | :--- | :--- |
| VV-P0-SW-001 | Profilo fail-closed | Lanciare `profile:=production` senza MCU. | Bridge non pubblica stato valido simulato. |
| VV-P0-SW-002 | CAN non simulato | Avviare VESC driver senza CAN in production. | Nodo fallisce o segnala fault, non simula. |
| VV-P0-SAFE-001 | Boot safe | Alimentare MCU con VESC collegati e ruote sollevate. | `motor_consent=false` al boot. |
| VV-P0-SAFE-002 | Heartbeat loss | Inviare comando moto, fermare bridge/Jetson. | Stop entro 500 ms. |
| VV-P0-SAFE-003 | E-stop fisico | Premere E-stop durante comando attivo. | Consenso off e fault latched. |
| VV-P0-SAFE-004 | CRC | Inviare frame command/status con CRC errato. | Frame rifiutato e fault loggato. |
| VV-P0-SAFE-005 | AI non safety | Disabilitare camera/YOLO durante movimento lento. | Safety primaria resta attiva e indipendente. |
| VV-P0-ELEC-001 | Bus 24 V | Review schema, BOM, parametri. | Nessuna voce 48 V non approvata. |
| VV-P0-ELEC-002 | Dump load | Batteria alta e rigenerazione controllata. | Bus sotto soglia, dump termicamente sicuro. |
| VV-P0-ELEC-003 | Protezioni rami | Ispezione schema e installazione. | Ogni ramo critico protetto. |
| VV-P0-ELEC-004 | Cablaggio | Continuita', isolamento, pull test leggero, vibrazione. | Nessun falso contatto o isolamento insufficiente. |
| VV-P0-MECH-001 | Stazionamento | Rover massa target su pendenza scelta. | Nessun movimento a batteria spenta. |
| VV-P0-MECH-002 | Tavole costruttive | Review tavole PDF/STEP/DXF. | Quote, tolleranze e revisioni presenti. |
| VV-P0-MECH-003 | Drivetrain CAD | Interference check catena ruota-albero-cuscinetto. | Zero interferenze, coassialita' accettata. |
| VV-P0-DATA-001 | Evidence pack | Eseguire un test banco con manifest. | Rosbag/JSONL/report generati e archiviati. |
| VV-P0-REX-001 | Baseline potenza REX | Review documenti, config e calcoli. | Target continuo 600-700 W e limiti coerenti. |
| VV-P0-REX-002 | Kill GX50 | E-stop, heartbeat loss, overspeed e Vdc alta con GX50 su banco. | Kill ignition attivo, generazione off e fault latched. |
| VV-P0-REX-003 | Parti rotanti REX | Runout/allineamento/tensione cinghia con guardie installate. | Nessun contatto, vibrazione anomala o allentamento. |
| VV-P0-REX-004 | Carica REX 24 V | Carico resistivo 100 W -> 700 W, BMS/SoC alto e no-load. | Vdc < 70 V, bus < 29.2 V, no backfeed. |
| VV-P0-REX-005 | Fuel/CO/fire | Checklist banco prima accensione. | CO monitor, ventilazione, leak check, estintore e scarico schermato. |
| VV-P1-REX-006 | Telemetria REX | Sim/replay con RPM, Vdc, corrente e fault. | `RangeExtenderStatus` coerente con `EnergyBudget`. |

## Report Minimo

Ogni test produce:

- `run_manifest.yaml`;
- log grezzo `rosbag2` o JSONL;
- foto o screenshot quando utile;
- risultato pass/fail;
- anomalia e decisione;
- commit hash e profilo config.
