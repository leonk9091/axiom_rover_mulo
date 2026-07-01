# System Requirements Specification - Mulo

Data baseline: 2026-06-14

## Regole

- Ogni requisito ha ID stabile `MULO-SYS-###`.
- Le formule devono restare leggibili in Unicode o testo semplice.
- Nessun requisito P0 e' considerato chiuso senza evidenza di test.

## Requisiti P0

| ID | Requisito | Acceptance criteria |
| :--- | :--- | :--- |
| MULO-SYS-001 | Il bus di trazione nominale e' 24 V finche' una decisione tecnica approvata non migra l'intero sistema a 48 V. | BOM, schema potenza, parametri ROS e firmware riportano 24 V nominali e range operativo coerente. |
| MULO-SYS-002 | Il rover deve partire con consenso motori disabilitato tramite safety MCU STM32 Nucleo. | Al boot STM32 e VESC alimentati, `motor_consent=false` fino ad arm esplicito. |
| MULO-SYS-003 | La perdita heartbeat Jetson/ROS deve portare il comando a zero entro 500 ms. | Test banco con comando attivo e arresto bridge: consenso off o velocita' zero entro 500 ms. |
| MULO-SYS-004 | E-stop fisico NC deve disabilitare la trazione indipendentemente da ROS. | Premuta E-stop durante comando attivo: fault latched e motor consent off. |
| MULO-SYS-005 | I frame Jetson -> MCU e MCU -> ROS devono avere CRC-16/CCITT-FALSE valido in profili reali. | `crc16=0` o CRC errato viene rifiutato e loggato come fault. |
| MULO-SYS-006 | La simulazione hardware deve essere esplicita e mai default in profili `bench`, `field`, `production`. | `simulate_without_serial=false` e `simulate_without_can=false` nei profili reali. |
| MULO-SYS-007 | Il drivetrain 4WD non deve comandare i motori se CAN/VESC o librerie runtime mancano in profilo reale. | Avvio senza CAN in `production` causa fault/fallimento nodo, non telemetria simulata. |
| MULO-SYS-008 | Freni meccanici devono tenere il rover fermo a batteria spenta sulla pendenza di test scelta. | Report stazionamento con massa target, carico e pendenza. |
| MULO-SYS-009 | Dump load deve gestire rigenerazione con batteria quasi piena senza sovratensione bus. | Test banco/discesa controllata con tensione bus sotto soglia massima. |
| MULO-SYS-010 | Ogni ramo potenza critico deve avere protezione dedicata. | Schema mostra fusibile batteria, VESC, DC-DC, carica, servizi e dump load. |
| MULO-SYS-011 | Cablaggi potenza, CAN e sensori critici devono avere sezione, connettore, pinout e strain relief documentati. | Wire list validata con continuita', isolamento e ispezione meccanica. |
| MULO-SYS-012 | Disegni CAD critici devono essere costruttivi prima degli ordini. | STEP/PDF quotati/DXF per telaio, albero, piastre, staffe freno, box, con tolleranze e revisione. |
| MULO-SYS-013 | La catena ruota -> mozzo -> disco -> albero -> UCF204 -> piastra -> telaio deve essere validata come assieme. | Review CAD con interferenze zero, coassialita' e accesso bulloni confermati. |
| MULO-SYS-014 | Ogni test banco e outdoor deve produrre log e manifest. | Rosbag/JSONL, commit, profilo config, operatore, ambiente e risultato archiviati. |
| MULO-SYS-015 | Nessuna AI visiva puo' essere safety primaria. | Safety primaria resta STM32 Nucleo + E-stop + ToF/IMU/geometria + consenso motori. |
| MULO-SYS-016 | E-stop fisico e fault critico devono spegnere anche il range extender Honda GX50 tramite kill ignition fail-safe. | Test banco con GX50 al minimo/generazione: E-stop, heartbeat loss e fault REX portano `engine_kill_request=true` e spegnimento fisico. |
| MULO-SYS-017 | Il ramo range extender deve avere protezione dedicata contro sovracorrente, backfeed, sovratensione e BMS charge inhibit. | Schema mostra fusibile ramo carica, diodo ideale/contattore, buck CC/CV, limite Vdc e interfaccia BMS. |
| MULO-SYS-018 | Nessuna prova con REX acceso e' ammessa senza guardie su cinghia, pulegge, frizione e BLDC outrunner. | Ispezione fisica e foto setup prima di ogni run con parti rotanti. |
| MULO-SYS-019 | Prove GX50 richiedono procedura fuel/CO/fire. | CO monitor, ventilazione, estintore, leak check, fuel shutoff e schermatura scarico firmati nel manifest. |

## Requisiti P1/P2

| ID | Requisito | Acceptance criteria |
| :--- | :--- | :--- |
| MULO-SYS-101 | Il progetto deve avere una CI che compila Python, esegue pytest, colcon e firmware PlatformIO. | Workflow verde su PR con artefatti test. |
| MULO-SYS-102 | Ogni release deve fissare versioni hardware, firmware, ROS, parametri e BOM. | Tag o release note con hash commit e profilo config. |
| MULO-SYS-103 | Il digital twin deve riprodurre scenari safety P0 prima dei test outdoor. | Scenario SIL per heartbeat loss, estop, pendenza, stallo, UWB loss e discesa. |
| MULO-SYS-104 | Cybersecurity va attivata prima di telemetria remota reale. | Threat model, SROS2 policy, chiavi e recovery playbook approvati. |
| MULO-SYS-105 | Il range extender deve avere telemetria minima dedicata prima dell'integrazione field. | `RangeExtenderStatus` pubblica stato, RPM, Vdc, corrente carica, throttle, fault e kill state. |
| MULO-SYS-106 | La baseline potenza REX deve essere unica. | Documenti, config e test usano target continuo 600-700 W, limiti 24 V e derating termico coerenti. |
