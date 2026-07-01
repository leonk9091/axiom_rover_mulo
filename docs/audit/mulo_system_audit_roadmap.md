# Audit e Roadmap di Sistema - Axiom Rover "Mulo"

Data audit: 2026-05-28

Questo documento consolida lo stato progettuale del rover **Mulo** e lo trasforma in una roadmap tecnica orientata al miglior rapporto costo-beneficio. Il target non e' un mezzo "low cost", ma una piattaforma da trekking realmente robusta: riparabile, sicura, diagnosticabile, capace di seguire l'operatore e predisposta a una modalita' sentinella statica non offensiva.

Per "mission-grade ruggedness" si intende: margine meccanico, protezioni elettriche, safety indipendente, componenti IP-rated, connettori bloccabili, derating termico, logging, test ripetibili, cyber-hardening e manutenzione semplice. Non si intende alcuna funzione offensiva.

## 1. Obiettivo Operativo

### Missione primaria

Il Mulo deve accompagnare un operatore su sentieri di trekking trasportando carico, mantenendo un comportamento prevedibile e fermandosi in modo sicuro quando sensori, potenza o software non sono affidabili.

Le funzioni obiettivo sono:

| Funzione | Descrizione | Vincolo safety |
| :--- | :--- | :--- |
| Follow-me | Inseguimento dell'operatore a passo umano tramite UWB/radio come riferimento locale principale. | Perdita UWB o target incoerente -> rallenta/stop, non inseguimento cieco. |
| Avanza su traccia | Avanzamento lento su segmento GPS/GNSS registrato o comando operatore. | GPS non deve comandare da solo il follow-me ravvicinato. |
| Recovery trekking | Gestione stallo, 3WD degradato, verricello, log fault e richiesta intervento. | Corrente alta + encoder fermi -> recovery breve, poi stop/SOS. |
| Sentry statica | Guardia campo notturna con termico/geometria, allerta e deterrenza luce/audio. | Nessun pattugliamento lineare notturno; yaw lento solo se sicuro. |
| Diagnostica | Log di corrente, tensione, temperatura, link, fault, stato sensori, missione. | Un guasto intermittente deve diventare visibile e riproducibile. |

### Fascia di progetto scelta

La fascia consigliata e' **Trekking serio**, stimata intorno a **4.000-5.500 EUR** se buona parte della carpenteria, integrazione e test viene gestita internamente. Questa fascia compra robustezza dove serve davvero:

- freni meccanici e dump load invece di affidarsi solo alla rigenerazione;
- batteria LiFePO4 con BMS adatto alla corrente continua;
- connettori IP e cablaggio serio;
- controller real-time separato dal computer ROS 2;
- sensori geometrici safety-first;
- logging e test prima di autonomia complessa.

## 2. Linee Architetturali Consolidate

Nel progetto esistono due linee che vanno trattate come livelli evolutivi, non come alternative confuse.

### MK0 - Base fisica robusta

MK0 e' la piattaforma fisica e embedded da rendere affidabile per prima:

- telaio articolato in acciaio S235 30x30x2 mm;
- ponte corazzato con piastra 6 mm, UCF204 esterno e alberi custom 42CrMo4;
- 4 motori brushless/ridotti 24 V 200 W con ruote cargo 20";
- freni meccanici a disco 203 mm con leve a cricchetto;
- LiFePO4 24 V con BMS, fusibili, sezionatore e cablaggio dimensionato;
- VESC/CAN, dump load, monitoraggio termico e derating;
- follow-me UWB/radio, GNSS per traccia/geofence, IMU, ToF anti-ostacolo;
- microcontrollore embedded per controllo critico, watchdog e logging compatto.

MK0 deve diventare il rover che cammina, frena, registra e si ferma bene anche senza AI complessa.

### X-1 - Upgrade cognitivo

X-1 aggiunge autonomia avanzata senza spostare la safety critica su Linux:

- Jetson Orin Nano Super 8 GB come base AI/ROS 2;
- STM32/H7 o equivalente per watchdog, stop indipendente, ToF safety, IMU e heartbeat;
- LiDAR 2D DToF schermato dal sole;
- camera RGB per semantica e teleoperazione;
- ToF multizona/singoli per vuoti, gradini e zone cieche;
- BNO085/BNO086 come IMU prototipo, IMU industriale come upgrade;
- 4G/LTE e LoRa per SOS, telemetria e fallback;
- ROS 2 con pacchetti `rover_control`, `rover_safety`, `rover_navigation`, `rover_power`, `rover_system`, `rover_interfaces`.

La Jetson decide contesto e traiettoria. Lo STM32 deve poter fermare il rover anche se Jetson, ROS 2 o la rete neurale falliscono.

## 3. Capitale del Sistema

### Asset gia' presenti nel repo

| Capitale | Stato | Valore pratico |
| :--- | :--- | :--- |
| Documentazione architetturale | Ampia e coerente | Chiarisce MK0, X-1, sentry, hardware trekking, sicurezza, ricarica e logistica. |
| BOM iniziale | Presente | Base per acquisti, ma da trasformare in distinta con fornitori, codici, quantita' e costi reali. |
| CAD/immagini meccaniche | Presente | Utile per layout e comunicazione, ma serve revisione quotata finale. |
| ROS 2 workspace | Presente | Struttura modulare corretta con interfacce custom e nodi separati. |
| Test unitari Python | Presenti | Baseline positiva: 13 test passati localmente. |
| Firmware ESP32 | Presente come base | Da portare da bozza/prototipo a firmware con protocollo stabile e test HIL. |
| Parametri globali | Presenti | `rover_params.yaml` centralizza valori principali, ma deve allinearsi alla configurazione hardware finale. |
| Diagrammi | Presenti | Buoni per onboarding e revisione tecnica. |

### Asset fisici da trattare come capitale critico

- **Telaio e drivetrain:** sono il cuore del valore del progetto. Il ponte corazzato protegge i riduttori dai carichi radiali, quindi ha beneficio costo/affidabilita' molto alto.
- **Freni e stazionamento:** componente safety di primo ordine. Non devono essere rinviati.
- **Cablaggio e connettori:** spesso sottostimati, ma determinano affidabilita' reale in acqua, fango e vibrazioni.
- **Batteria e BMS:** scegliere LiFePO4 robusta riduce rischio incendio, degrado e instabilita' sotto carico.
- **Safety MCU:** capitale funzionale, non accessorio. E' il confine tra prototipo e mezzo credibile.
- **Log e dati missione:** ogni test outdoor deve produrre dati: senza log il progetto resta dipendente da impressioni.

## 4. Audit di Maturita'

Legenda:

- **Documentato:** definito nei documenti, non necessariamente realizzato.
- **Simulato/testato:** coperto da test software o comportamento simulato.
- **Prototipo:** esiste una prima implementazione o base firmware/software.
- **Da validare su hardware:** richiede prove su componenti fisici reali.

| Sottosistema | Maturita' | Evidenza | Nota audit |
| :--- | :--- | :--- | :--- |
| Telaio S235 e snodo centrale | Documentato | Specifiche MK0 e disegni | Serve revisione quote, tolleranze, saldature e peso reale. |
| Ponte corazzato / alberi 42CrMo4 | Documentato | Specifiche hardware e CAD | Alta priorita': lavorazione e tolleranze h6 sono decisive. |
| Powertrain 4WD | Documentato + simulato in cinematica | `test_kinematics.py`, VESC driver | Da validare con VESC/CAN reali, termica e stallo. |
| Freni meccanici | Documentato | Performance/safety | Non risultano test fisici; obbligatori prima di pendenze reali. |
| Dump load | Documentato | Power monitor e docs | Da dimensionare, montare e provare con batteria carica. |
| Batteria/BMS | Documentato | BOM e docs power | Scelta finale non congelata; serve scheda tecnica reale. |
| Safety watchdog ROS | Simulato/testato | Nodo `safety_watchdog`, test | Buona base, ma non sostituisce STO/E-stop hardware. |
| Hardware bridge | Simulato/testato | Nodo `hardware_bridge`, bridge model | Protocollo seriale da rendere definitivo e verificare su MCU. |
| Firmware ESP32/STM32 | Prototipo | Firmware e pseudo-codice docs | Va consolidato con heartbeat, stato fault, watchdog e test HIL. |
| Follow-me UWB | Documentato | Geometria UWB | Mancano calibrazione fisica, gestione outlier e prove outdoor. |
| Percezione AI Jetson | Documentato/prototipo software | `follow_me.py` contiene placeholder YOLO/depth | Da implementare realmente o tenere fuori dalla safety. |
| Terrain assessment | Prototipo | Nodo e test navigation | Da collegare a sensori reali e soglie verificabili. |
| Power EKF/ECMS | Simulato/testato | `power_monitor`, `test_energy.py` | Buona base algoritmica, da calibrare su batteria reale. |
| Modalita' sentry | Documentato | `mulo_future_sentry_mode.md` | Sicura se statica; da implementare solo dopo baseline safety. |
| Cybersecurity | Raccomandata | Engineering recommendations | Da pianificare dopo bringup stabile, prima di telemetria remota reale. |

## 5. Gap Critici

### Gap P0 - Da chiudere prima dei test outdoor seri

1. **E-stop fisico e Safe Torque Off reale**
   - Rischio: un bug ROS, freeze Jetson o fault CAN potrebbe lasciare coppia ai motori.
   - Mitigazione: circuito fisico indipendente che interrompe consenso ai driver o alimentazione comando; E-stop fungo accessibile; test di perdita heartbeat.

2. **Freni meccanici e stazionamento**
   - Rischio: rover non bloccato a batteria spenta o in discesa con rigenerazione non disponibile.
   - Mitigazione: 4 dischi 203 mm, pinze regolabili, leveraggi testati, procedura di stazionamento.

3. **Dump load e gestione rigenerazione**
   - Rischio: batteria piena + discesa -> sovratensione bus o perdita frenata rigenerativa.
   - Mitigazione: resistenza di frenatura dimensionata, fusibile, carter termico, soglie firmware, test con batteria sopra 95%.

4. **Cablaggio potenza e CAN rugged**
   - Rischio: guasti intermittenti da vibrazione, acqua, massa rumorosa, caduta tensione.
   - Mitigazione: cavi dimensionati per corrente continua, pressacavi, connettori IP67/IP68, twist CAN, terminazioni, strain relief.

5. **Validazione termica**
   - Rischio: tagli improvvisi per surriscaldamento in salita lenta o stop-and-go.
   - Mitigazione: sonde motori/VESC/batteria, derating progressivo, test salita lenta a carico reale.

### Gap P1 - Necessari per autonomia trekking affidabile

6. **Safety MCU reale**
   - Deve leggere E-stop, IMU, ToF safety, encoder/corrente, heartbeat Jetson e poter fermare indipendentemente.

7. **Protocollo Jetson -> STM32**
   - Interfaccia minima congelata in [Protocollo Safety MCU](mulo_safety_mcu_protocol.md): `desired_linear_velocity_ms`, `desired_angular_velocity_rads`, `mode`, `timeout_ms`, `seq`, `crc16`.
   - Se il comando scade, MCU ferma il rover.

8. **Calibrazione UWB e sensori**
   - UWB: distanza anchor, offset, outlier, perdita tag.
   - LiDAR/camera: estrinseca stabile.
   - ToF: soglie per vuoti, gradini, ostacoli bassi e sole diretto.

9. **Logging missione**
   - Log minimi: fault, temperatura, corrente, tensione, SoC, link, UWB/GNSS, IMU, comandi, stop safety, eventi sentry.

10. **Test outdoor progressivi**
   - Prima piano e bassa velocita', poi ghiaia, salita, discesa, fango, sole/ombra, carico, stallo controllato.

## 6. Le 10 Decisioni Prioritarie

| # | Decisione | Raccomandazione | Motivo costo-beneficio |
| ---: | :--- | :--- | :--- |
| 1 | MCU safety | STM32/H7 o scheda robusta equivalente, non solo ESP32 per safety finale | Determinismo, I/O, watchdog e crescita futura. |
| 2 | Batteria | LiFePO4 24 V 50-100 Ah smart se budget consente | Sicurezza, cicli, corrente continua, autonomia reale. |
| 3 | Freni | Meccanici a disco 203 mm con comando manuale bloccabile | Riduce il rischio piu' grave: perdita stazionamento. |
| 4 | Dump load | Obbligatorio con VESC e discese | Evita sovratensione e perdita frenata a batteria piena. |
| 5 | Controller motori | VESC/CAN di fascia affidabile, dissipati su alluminio | Risparmiare qui genera fault intermittenti e termici. |
| 6 | Connettori | IP67/IP68 bloccabili per potenza, motori, sensori critici | Grande beneficio reale in vibrazione/fango/acqua. |
| 7 | LiDAR base | LD19 o DToF equivalente schermato, upgrade solo se test fallisce | Buon costo-beneficio per occupancy e ostacoli. |
| 8 | Camera | RGB USB stabile; global shutter solo se il budget lo permette | La camera e' semantica, non safety primaria. |
| 9 | Sentry | MLX90640 + LoRa pager dopo safety baseline | Basso consumo e valore pratico, ma non prima della trazione sicura. |
| 10 | Software hardening | CI, test, rosbag/log, simulazione SIL prima di AI avanzata | Aumenta affidabilita' senza comprare hardware premium. |

## 7. Matrice Costo-Beneficio

### Comprare o costruire subito

| Voce | Stima | Beneficio | Priorita' |
| :--- | ---: | :--- | :--- |
| Freni meccanici completi | 180-450 EUR | Stazionamento e discesa sicura | P0 |
| Cablaggio/connettori/scatole IP | 250-500 EUR | Riduzione guasti intermittenti | P0 |
| Dump load + protezioni | 80-220 EUR | Frenata rigenerativa sicura | P0 |
| Safety MCU + I/O + transceiver | 70-180 EUR | Stop indipendente da Jetson/ROS | P0 |
| Sonde termiche + montaggio | 30-120 EUR | Derating prima del fault | P0 |
| Log SD/telemetria base | 20-100 EUR | Diagnostica e test ripetibili | P1 |

### Comprare dopo baseline

| Voce | Stima | Quando ha senso |
| :--- | ---: | :--- |
| Jetson Orin Nano Super | 280-330 EUR | Dopo trazione, safety MCU e sensoristica base. |
| LiDAR migliore | +300-1.500 EUR | Solo se LD19/DToF economico fallisce nei test outdoor. |
| Orin NX 16 GB | +350-800 EUR | Se i modelli AI saturano Nano e la pipeline e' gia' stabile. |
| IMU industriale | +150-800 EUR | Se BNO085/BNO086 mostra deriva/vibrazioni non accettabili. |
| Depth camera outdoor | +300-1.000 EUR | Se camera RGB + LiDAR 2D non basta per avoidance/teleop. |

### Evitare nella fase attuale

| Voce | Motivo |
| :--- | :--- |
| Pattugliamento sentry notturno | Rischio tiranti tende, ostacoli sottili e collisioni notturne. |
| Pannelli solari fissi sul rover | Aumentano CoM, si danneggiano e rendono poco su sentiero ombreggiato. |
| RTX/mini PC ad alto consumo | Potenza alta ma peso, calore e alimentazione sfavorevoli. |
| Autonomia basata solo su camera RGB | Non safety-safe in buio, polvere, pioggia, controluce. |
| Componenti premium non test-driven | Aumentano costo senza sapere quale collo di bottiglia e' reale. |

## 8. Roadmap di Sviluppo

### Fase 0 - Baseline dati e distinta

Obiettivo: congelare cosa si sta costruendo.

- Aggiornare BOM con quantita', costo reale, fornitore, link, massa, tensione/corrente, stato acquisto.
- Allineare `rover_params.yaml` con configurazione fisica scelta: massa, batteria, ruota, track width, limiti.
- Definire checklist di test e log minimi.
- Output: distinta ordinabile, schema elettrico di potenza, schema segnali, piano test banco.

### Fase 1 - Base meccanica sicura

Obiettivo: rover movimentabile, trainabile e bloccabile.

- Costruire/verificare telaio S235, snodo, ponte corazzato e alberi.
- Montare ruote, UCF204/UCP204, freni, leveraggi e quick-split.
- Eseguire prove statiche: carico, torsione, stazionamento, traino limp-home.
- Output: piattaforma rolling chassis con freni certificati da test interno.

### Fase 2 - Potenza, trazione e safety fisica

Obiettivo: movimento controllato a bassa velocita' con stop indipendente.

- Installare batteria, fusibili, sezionatore, DC-DC, VESC, CAN, dump load.
- Integrare E-stop fisico e consenso motori indipendente.
- Validare VESC driver, telemetria, timeout comando e stop su fault.
- Test: piano, salita leggera, discesa con batteria carica, stallo controllato, perdita CAN.

### Fase 3 - MCU safety e firmware

Obiettivo: STM32/MCU come garante real-time.

- Definire protocollo Jetson/ROS -> MCU: velocita', yaw, mode, timeout.
- Usare [Protocollo Safety MCU](mulo_safety_mcu_protocol.md) come contratto di implementazione per firmware e `hardware_bridge`.
- MCU legge E-stop, IMU, ToF safety, corrente/encoder, link heartbeat.
- MCU pubblica stato compatto verso ROS: safety state, fault, degraded mode.
- Test HIL: heartbeat perso, sensore stale, pendenza critica, vuoto, corrente alta.

### Fase 4 - Follow-me affidabile

Obiettivo: seguire operatore senza AI fragile.

- Implementare/calibrare UWB anchor-tag.
- Calcolare vettore operatore con filtri temporali e rejection outlier.
- Policy: UWB valido -> follow; UWB degradato -> rallenta/stop; GPS solo logging e traccia.
- Test outdoor: area aperta, bosco, cambio direzione, perdita tag, operatore troppo vicino.

### Fase 5 - Autonomia trekking assistita

Obiettivo: avanzamento su traccia e avoidance semplice.

- Integrare LiDAR 2D, ToF, IMU, odometria e camera RGB su ROS 2.
- Costmap e shared autonomy con limiti velocita' conservativi.
- Riconoscimento persona/ostacoli solo come semantica, non come safety primaria.
- Test: ostacoli bassi, ostacoli alti, persone che attraversano, bordo sentiero simulato.

### Fase 6 - Sentry statica non offensiva

Obiettivo: guardia campo a bassissimo consumo senza rischio movimento lineare.

- Sensore termico MLX90640 + ToF/LiDAR lento per conferma geometrica.
- LoRa pager con stato verde/giallo/rosso, vibrazione e batteria rover.
- Deterrenza: fari LED strobo e ultrasuoni/multifrequenza entro limiti locali.
- Movimento: solo yaw lento, `ω_max ≈ 5 deg/s`, se freni/terreno/safety lo consentono.
- Test: falsi positivi termici, persone, animali domestici, vento, pioggia, tende/tiranti.

### Fase 7 - Hardening mission-grade

Obiettivo: robustezza operativa e manutenzione.

- SROS2/DDS security per reti operative.
- Secure firmware update e versionamento configurazioni.
- Rosbag/log compressi per ogni missione.
- Manutenzione predittiva semplice: ore motore, temperatura max, corrente max, fault count, vibrazioni.
- Manuale operativo: pre-check, post-check, recovery, limp-home, ricarica, sentry.

## 9. Interfacce Future da Consolidare

Questa attivita' non modifica API, messaggi o firmware. Le seguenti interfacce vanno pero' rese stabili prima del passaggio X-1:

### Comando Jetson -> STM32

```text
seq
desired_linear_velocity_ms
desired_angular_velocity_rads
mode
timeout_ms
crc16
```

Regola: se `timeout_ms` scade o heartbeat Jetson manca per circa 500 ms, STM32 porta il comando a zero e richiede stop controllato. Il dettaglio operativo e' definito in [Protocollo Safety MCU](mulo_safety_mcu_protocol.md).

### Stati missione

```text
manual
trek_follow
advance_trace
degraded
sentry_static
estop
```

### Log missione minimo

```text
timestamp
mission_mode
fault_code
estop_state
motor_current_a
motor_temp_c
esc_temp_c
battery_voltage_v
battery_soc
uwb_valid
gnss_valid
link_state
roll_pitch_yaw
cmd_velocity
measured_velocity
sentry_event
```

## 10. Risk Register

| Rischio | Impatto | Probabilita' | Mitigazione verificabile |
| :--- | :--- | :--- | :--- |
| Perdita frenata in discesa | Critico | Media | Freni meccanici + dump load testato con batteria carica. |
| Fault software lascia comando attivo | Critico | Media | MCU safety con heartbeat e consenso motori indipendente. |
| Guasto intermittente cablaggio | Alto | Alta | Connettori IP, strain relief, log fault, test vibrazione. |
| Surriscaldamento VESC/motori | Alto | Media | Sonde, dissipatori, derating, test salita lenta a carico. |
| UWB instabile in bosco/rocce | Medio | Media | Filtri, timeout, stop su incoerenza, GPS non usato per follow ravvicinato. |
| LiDAR/ToF degradati dal sole | Medio | Media | Paraluce, filtri outlier, test outdoor, fallback stop. |
| AI visiva sbaglia classe | Medio | Alta | Camera non safety primaria; decisioni critiche su geometria/MCU. |
| Sentry genera falsi allarmi | Basso/medio | Media | Conferma termico + geometrico + isteresi temporale. |
| Peso eccessivo | Medio | Media | Quick-split, pesatura reale, rimozione componenti non essenziali. |
| Budget disperso in upgrade prematuri | Alto | Alta | Acquisti legati a test falliti o gap P0/P1. |

## 11. Acceptance Criteria

Il progetto entra in stato "trekking serio" solo quando:

- freni meccanici bloccano il rover a batteria spenta su pendenza di test;
- E-stop fisico ferma la trazione anche se ROS 2 non risponde;
- perdita heartbeat Jetson/ROS porta a stop entro circa 500 ms lato MCU;
- dump load gestisce una discesa con batteria quasi piena senza sovratensione;
- log missione consente di ricostruire almeno gli ultimi 10 minuti prima di un fault;
- follow-me si ferma in modo prevedibile su perdita UWB;
- cablaggi e box resistono a vibrazione, fango e pioggia leggera;
- test unitari software continuano a passare;
- ogni uscita outdoor produce checklist pre/post e dati archiviati.

## 12. Conclusione

Il progetto ha gia' una base documentale e software superiore a un normale prototipo hobbistico. Il punto critico ora non e' aggiungere piu' AI o piu' funzioni, ma trasformare la piattaforma in un sistema fisico verificabile.

La sequenza a miglior costo-beneficio e':

1. rendere sicuri trazione, freni, alimentazione e cablaggio;
2. separare davvero safety MCU da ROS 2/Jetson;
3. validare follow-me UWB e logging;
4. aggiungere autonomia trekking con sensori geometrici;
5. introdurre sentry statica solo dopo che stop, freni e alimentazione sono affidabili.

Questa strada evita spese premature e porta il Mulo verso una robustezza da missione: non spettacolare sulla carta, ma credibile sul sentiero.
