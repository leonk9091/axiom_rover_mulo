# Checklist P0 Pre-Acquisto - Mulo Trekking

Data: 2026-05-28

Questa checklist serve prima di scegliere o comprare i componenti. L'obiettivo e' evitare acquisti incompatibili, sottodimensionati o inutilmente premium. Una voce P0 non chiusa indica che la scelta del pezzo rischia di essere prematura.

## Regola Base

Prima si congelano requisiti, interfacce e test. Poi si scelgono i pezzi.

Per ogni componente candidato devono essere noti:

- tensione nominale e range operativo;
- corrente continua reale, non solo picco;
- massa e ingombro;
- temperatura operativa;
- tipo connettori;
- compatibilita' meccanica/elettrica/software;
- rischio se fallisce;
- test con cui verra' accettato.

## P0.1 Architettura Elettrica

| Check | Criterio di accettazione | Stato |
| :--- | :--- | :--- |
| Tensione bus DC scelta | 24 V nominali confermati per batteria, VESC, carica, DC-DC e dump load. | Da chiudere |
| Corrente continua stimata | Corrente trazione continua e picco calcolate per 4 motori + margine. | Da chiudere |
| Fusibile principale | Taglia, posizione e tipo definiti vicino alla batteria. | Da chiudere |
| Sezionatore manuale | Deve scollegare il bus potenza in modo accessibile e sicuro. | Da chiudere |
| Rami protetti | Ogni ramo critico ha fusibile o protezione: VESC, carica, DC-DC, servizi. | Da chiudere |
| Masse e ground strategy | Separazione ragionata tra potenza, logica e segnali sensibili. | Da chiudere |
| Box elettrici | IP rating, pressacavi, accesso fusibili e scarico condensa definiti. | Da chiudere |

## P0.2 Safety Fisica

| Check | Criterio di accettazione | Stato |
| :--- | :--- | :--- |
| E-stop fisico | Pulsante reale accessibile che non dipende da ROS 2. | Da chiudere |
| Consenso motori | Linea/circuito che disabilita coppia ai controller anche se il software fallisce. | Da chiudere |
| Stato safe all'avvio | Il rover parte con trazione disabilitata finche' safety e comandi non sono validi. | Da chiudere |
| Timeout comando | Perdita heartbeat/comando per circa 500 ms -> velocita' zero/stop controllato. | Da chiudere |
| Freni meccanici | Stazionamento a batteria spenta su pendenza di test. | Da chiudere |
| Dump load | Frenata rigenerativa gestibile con batteria quasi piena. | Da chiudere |
| Procedura recovery | Come isolare un motore, trainare, spegnere, riaccendere e loggare fault. | Da chiudere |

## P0.3 Meccanica Critica

| Check | Criterio di accettazione | Stato |
| :--- | :--- | :--- |
| Massa target | Massa realistica con batteria, carico, freni, cablaggio e box. | Da chiudere |
| Disegni quotati | Telaio, snodo, piastre, alberi e staffe hanno quote e tolleranze. | Da chiudere |
| Ponte corazzato | Il carico radiale ruota scarica su UCF204/telaio, non sul riduttore. | Da chiudere |
| Alberi custom | Materiale, cava chiavetta, flangia 6 fori, diametri e tolleranza h6 definiti. | Da chiudere |
| Freni e flange | Disco e trasmissione non interferiscono sul mozzo 6 fori. | Da chiudere |
| Quick-split | Separazione semitelai gestibile senza tagliare cablaggi o sforzi eccessivi. | Da chiudere |
| Accesso manutenzione | Fusibili, VESC, motori, batteria e pinze freno accessibili sul campo. | Da chiudere |

## P0.4 Firmware e Controllo Basso Livello

| Check | Criterio di accettazione | Stato |
| :--- | :--- | :--- |
| MCU safety scelta | STM32/H7 o equivalente con I/O sufficienti, watchdog e comunicazioni robuste. | Da chiudere |
| Protocollo comando | Definito in [Protocollo Safety MCU](mulo_safety_mcu_protocol.md): seq, velocita', yaw, mode, timeout_ms, estop_request, enable_motors_request, crc16. | Definito, da implementare |
| Protocollo stato | Definito in [Protocollo Safety MCU](mulo_safety_mcu_protocol.md): safety_state, estop, motor_consent, fault_code, degraded_mode, sensor_validity, heartbeat_age, crc16. | Definito, da implementare |
| Stop locale | MCU puo' portare comandi a zero senza aspettare Jetson. | Da chiudere |
| Lettura sensori safety | IMU, ToF critici, corrente/encoder o stato motori disponibili al MCU. | Da chiudere |
| Logging minimo MCU | Fault, timestamp, estop, tensione, corrente, temperatura, link, modo missione. | Da chiudere |

## P0.5 Piano Test Prima del Terreno

| Test | Pass/fail minimo | Stato |
| :--- | :--- | :--- |
| Accensione senza trazione | Nessun motore gira finche' consenso e comando non sono validi. | Da preparare |
| E-stop | Trazione disabilitata immediatamente e fault latched. | Da preparare |
| Perdita heartbeat | Stop entro circa 500 ms. | Da preparare |
| Ruote sollevate | Comandi avanti/indietro/rotazione coerenti e limitati. | Da preparare |
| Perdita CAN o VESC | Stop/degraded mode senza comandi casuali. | Da preparare |
| Sovracorrente/stallo | Recovery breve o stop, con log. | Da preparare |
| Dump load | Attivazione sopra soglia con batteria alta, senza sovratensione. | Da preparare |
| Freni meccanici | Rover fermo in stazionamento su pendenza scelta. | Da preparare |

## Output da Produrre Prima degli Acquisti

1. BOM decisionale compilata con almeno 2-3 candidati per le categorie critiche.
2. Schema elettrico preliminare: batteria -> fusibili -> sezionatore -> bus DC -> VESC/DC-DC/MCU/Jetson/dump load.
3. Disegni quotati della catena telaio-piastra-cuscinetto-albero-ruota.
4. Protocollo safety Jetson/STM32 in forma tabellare: [Protocollo Safety MCU](mulo_safety_mcu_protocol.md).
5. Piano test banco firmato come criterio di accettazione.

## Criterio di Prontezza

Si puo' iniziare a comprare quando:

- tutte le voci P0 hanno una scelta tecnica o un criterio misurabile;
- ogni componente costoso ha almeno un'alternativa confrontata;
- i pezzi safety non dipendono da componenti ancora incerti;
- ogni acquisto ha una prova di accettazione associata.
