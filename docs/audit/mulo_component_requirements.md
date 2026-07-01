# Requisiti Minimi Componenti - Mulo Trekking

Data: 2026-05-28

Questo documento definisce i requisiti tecnici minimi per scegliere i componenti. Non contiene marchi obbligatori: serve a confrontare i pezzi candidati prima dell'acquisto.

## Principi di Scelta

- Preferire componenti con dati continui reali rispetto a valori di picco pubblicitari.
- Spendere dove un guasto ferma o rende pericoloso il rover: freni, batteria, controller, cablaggio, MCU safety, connettori, dissipazione.
- Rimandare upgrade AI/percezione premium finche' trazione, safety e logging non sono affidabili.
- Ogni pezzo critico deve avere un test di accettazione.

## Batteria e BMS

| Requisito | Minimo accettabile | Preferibile trekking serio |
| :--- | :--- | :--- |
| Chimica | LiFePO4 | LiFePO4 smart con Bluetooth o telemetria |
| Tensione | 24 V nominali, 8S LiFePO4 | 24 V nominali con curve e BMS documentati |
| Capacita' | 30 Ah per prototipo leggero | 50-100 Ah secondo massa/autonomia |
| Corrente continua | >= corrente continua richiesta da 4 motori + servizi | >= 100 A se si punta a batteria 100 Ah robusta |
| Protezioni | BMS con over/under-voltage, over-current, temperatura | BMS con temperatura celle, bilanciamento e log/app |
| Temperatura carica | Blocco carica sotto 0 gradi C | Auto-riscaldamento o procedura di preriscaldo |
| Montaggio | Case fissato e protetto da urti | Case IP/rugged con guide antivibrazione |
| Test accettazione | Scarica controllata e verifica cut-off BMS | Log tensione/corrente/temperatura sotto carico reale |

## Controller Motori / VESC

| Requisito | Minimo accettabile | Preferibile trekking serio |
| :--- | :--- | :--- |
| Comunicazione | CAN o interfaccia robusta equivalente | CAN con telemetria fault completa |
| Corrente continua | Compatibile con motori e salita lenta | Margine termico documentato e dissipatore esterno |
| Tensione | Compatibile con bus 24 V e picchi rigenerativi | Range con margine oltre tensione fine carica |
| Telemetria | RPM, corrente, tensione, temperatura, fault | Telemetria a 20 Hz o piu' con fault code chiari |
| Frenata | Supporto regen/brake current | Supporto dump load o gestione bus sovratensione |
| Montaggio | Dissipazione su piastra metallica | Pad/pasta termica, flusso aria protetto, sonde |
| Test accettazione | Ruote sollevate, comando RPM, stop e fault | Salita lenta a carico + discesa con batteria alta |

## Motori e Riduttori

| Requisito | Minimo accettabile | Preferibile trekking serio |
| :--- | :--- | :--- |
| Potenza | Circa 200 W per ruota | Potenza continua documentata, non solo nominale |
| Velocita' | Circa 4 km/h con ruote 20" | Coerente con passo trekking e controllo a bassa velocita' |
| Coppia | Sufficiente per 15-20 gradi con margine | Margine su massa reale e carico utile |
| Sensori | Hall/encoder o telemetria velocita' affidabile | Sensori integrati robusti e connettori bloccabili |
| Albero | Compatibile con albero custom e chiavetta | Geometria documentata e tolleranze certe |
| Termica | Carcassa monitorabile con sonda | Soglia derating conservativa validata |
| Test accettazione | Corrente, RPM e temperatura in banco | Stallo controllato e salita lenta con carico |

## Freni Meccanici

| Requisito | Minimo accettabile | Preferibile trekking serio |
| :--- | :--- | :--- |
| Tipo | Disco meccanico con comando Bowden | Pinze affidabili/regolabili, dischi 203 mm |
| Stazionamento | Leva o blocco meccanico indipendente dalla batteria | Leva a cricchetto o sistema equivalente |
| Ridondanza | Frenata su tutte le ruote o schema equivalente | 4 ruote con regolazione indipendente |
| Manutenzione | Regolabile sul campo | Ricambi e attrezzi comuni |
| Test accettazione | Rover fermo a batteria spenta su pendenza test | Test con massa target e carico utile |

## Cablaggio, Connettori e Box

| Requisito | Minimo accettabile | Preferibile trekking serio |
| :--- | :--- | :--- |
| Cavi potenza | Sezione per corrente continua, isolamento robusto | Silicone/automotive, guaina PA12, strain relief |
| Connettori potenza | Corrente nominale adeguata e polarizzazione | IP67/IP68, bloccabili o a baionetta |
| Connettori segnale | Bloccabili, non USB libero in zone vibranti | M8/M12/JST locking/automotive secondo area |
| CAN | Coppia twistata, terminazioni corrette | Schermatura e transceiver protetti/isolati |
| Box | Separazione logica/potenza, IP e accesso manutenzione | Pressacavi, scarico condensa, fissaggi antivibrazione |
| Test accettazione | Continuita', isolamento, vibrazione manuale | Test sotto carico, pioggia leggera/fango controllato |

## Safety MCU

Il contratto di comunicazione e i test minimi sono definiti in
[Protocollo Safety MCU](mulo_safety_mcu_protocol.md). Ogni scheda candidata
deve poter implementare quel protocollo con watchdog hardware, CRC/sequence
number e uscita consenso motori fail-safe.

| Requisito | Minimo accettabile | Preferibile trekking serio |
| :--- | :--- | :--- |
| MCU | STM32/H7 o equivalente real-time | Board con I/O abbondante e watchdog hardware |
| I/O | E-stop, ToF, IMU, encoder/corrente, consenso motori | Bus separati per sensori critici e diagnostica |
| Comunicazioni | UART/CAN verso Jetson/ROS | CAN o seriale robusta con CRC/sequence number |
| Watchdog | Timeout comandi circa 500 ms | Watchdog hardware + software + stato latched |
| Output safety | Linea consenso motori o STO equivalente | Uscita fail-safe con default disabilitato |
| Test accettazione | Perdita Jetson -> stop locale | Test HIL di sensori stale, estop, fault e reboot |

## Jetson / Computer ROS 2

| Requisito | Minimo accettabile | Preferibile trekking serio |
| :--- | :--- | :--- |
| Compute | Jetson Orin Nano Super 8 GB o equivalente | Orin NX solo se Nano diventa collo di bottiglia |
| Storage | NVMe/SD affidabile per log | NVMe fissato e raffreddato |
| Alimentazione | DC-DC stabile e separato dai disturbi motori | Filtro, fusibile e monitor tensione |
| Ruolo | Navigazione, AI, log, mission logic | Mai unico garante safety |
| Test accettazione | Crash/reboot Jetson non lascia motori attivi | Rosbag e recovery automatico controllato |

## Sensori Trekking

| Categoria | Minimo accettabile | Preferibile trekking serio |
| :--- | :--- | :--- |
| UWB | Anchor/tag con distanza stabile a corto raggio | Filtri outlier e calibrazione geometria anchor |
| GNSS | Logging traccia e coordinate | Antenna migliore e geofence, non follow primario |
| LiDAR 2D | DToF economico schermato dal sole | Upgrade solo se test outdoor fallisce |
| Camera RGB | USB stabile, lente non estrema | Global shutter se vibrazioni/rolling shutter danno problemi |
| ToF safety | VL53L5CX/VL53L1X per vuoti e zone cieche | Multiplexer/bus ordinato e soglie conservative |
| IMU | BNO085/BNO086 vicino al baricentro | IMU industriale se vibrazioni/deriva sono eccessive |

## Sentry Non Offensiva

| Requisito | Minimo accettabile | Preferibile trekking serio |
| :--- | :--- | :--- |
| Movimento | Nessun pattugliamento lineare notturno | Solo yaw lento se safety consente |
| Termico | MLX90640 o equivalente | Conferma con geometria ToF/LiDAR |
| Allerta | LoRa/pager con vibrazione | Stato verde/giallo/rosso, batteria e direzione |
| Deterrenza | LED e audio non offensivi | Sequenza graduata e configurabile |
| Energia | Consumo statico molto basso | Modalita sleep/low-rate e log eventi |
| Test accettazione | Falsi positivi e mancati rilevamenti documentati | Test con tende, tiranti, vento, persone e animali domestici |

## Template di Valutazione Pezzo

Ogni pezzo candidato deve rispondere a queste domande:

1. Quale requisito minimo soddisfa?
2. Che margine ha rispetto al requisito?
3. Quale guasto evita o riduce?
4. Cosa succede se fallisce?
5. Ha dati di corrente/temperatura continui?
6. Come si collega fisicamente ed elettricamente?
7. E' riparabile/sostituibile sul campo?
8. Quale test lo accetta o lo boccia?
9. Esiste alternativa piu' economica con rischio accettabile?
10. E' necessario ora o puo' aspettare una fase successiva?
