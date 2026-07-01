# MULO-REX Range Extender Readiness - Honda GX50

Data baseline: 2026-06-14

## Decisione

Il range extender Honda GX50 e' un sottosistema opzionale, separato dalla safety primaria di trazione. Non abilita test outdoor finche' il rover non e' gia' safe su batteria, freni, cablaggi e logging.

Baseline REX:

- Motore: Honda GX50, 47.9 cm3, 1.47 kW @ 7000 rpm, 2.2 Nm @ 5000 rpm.
- Target elettrico continuo: 600-700 W reali verso batteria 24 V LiFePO4.
- Architettura: GX50 -> frizione centrifuga -> HTD 5M -> BLDC outrunner -> raddrizzatore trifase -> DC link -> buck CC/CV -> diodo ideale -> batteria.
- Controllo: STM32 REX controller con setpoint corrente, feedback corrente carica, RPM, Vdc grezza, kill ignition.
- Stato iniziale enterprise: P0 aperto. REX disabilitato in tutti i profili finche' i test banco non sono firmati.

## Task Enterprise

| ID | Priorita | Task | Output richiesto |
| :--- | :--- | :--- | :--- |
| MULO-REX-T01 | P0 | Congelare baseline potenza | Target continuo, picco, duty cycle, derating termico e limiti RPM/Vdc. |
| MULO-REX-T02 | P0 | Disegno assieme meccanico | Piastra 5-6 mm, distanziali GX50, staffa BLDC, asole tensionamento, KP08, guardia cinghia. |
| MULO-REX-T03 | P0 | Validazione parti rotanti | Runout, allineamento pulegge, tensione cinghia, roll pin, contenimento rottura. |
| MULO-REX-T04 | P0 | Schema potenza REX | Fusibile ramo carica, sezionamento, raddrizzatore, condensatori 100 V, buck CC/CV, diodo ideale, BMS charge inhibit. |
| MULO-REX-T05 | P0 | Kill engine fail-safe | E-stop, heartbeat loss, overspeed, Vdc alta, no-current-with-throttle portano kill ignition. |
| MULO-REX-T06 | P0 | Procedura fuel/CO/fire | CO monitor, ventilazione, leak check, estintore, scarico caldo, fuel shutoff. |
| MULO-REX-T07 | P1 | Telemetria REX ROS | `RangeExtenderStatus`, RPM, Vdc, Icharge, throttle, fault, kill, temperature. |
| MULO-REX-T08 | P1 | ECU STM32 REX | PID corrente, input capture RPM, ACS758/INA226, servo throttle, relay kill, watchdog. |
| MULO-REX-T09 | P1 | Report rigenerabili | Manifest, log JSONL/rosbag, grafici Vdc/I/T/RPM/fault, commit e profilo. |

## Requisiti Di Safety

- Il kill ignition deve essere fisicamente fail-safe: in fault il relay/opto mette a massa l'accensione o porta il sistema in arresto equivalente documentato.
- L'E-stop fisico deve spegnere trazione e REX, non solo pubblicare un topic ROS.
- Se `RangeExtenderStatus.fault_code != NONE`, `rover_power` deve comandare `engine_kill_request=true` e `generation_enable=false`.
- Il ramo carica REX deve essere disaccoppiato dalla batteria con diodo ideale o contattore equivalente, per impedire backfeed a motore spento.
- Nessuna prova con GX50 acceso senza guardie su cinghia, pulegge, frizione e rotore BLDC.
- Nessuna prova indoor o in area riparata senza ventilazione e CO monitor attivo.

## Interfacce ROS

Input verso `rover_power`:

- `battery/voltage`
- `battery/current`
- `system/power_demand_w`
- `power/thermal_headroom`
- `range_extender/rpm`
- `range_extender/dc_link_voltage`
- `range_extender/charge_current`

Output da `rover_power`:

- `hardware/ice_generator_start`
- `hardware/ice_generator_kill`
- `hardware/range_extender_charge_current_a`
- `hardware/range_extender_throttle_request`
- `range_extender/status`
- `power/energy_budget`

Il bridge seriale aggiunge un CRC ausiliario `aux_crc16` per i comandi REX/dump-load. Il CRC trazione `crc16` resta separato per compatibilita' con il safety command.

## Gate Prima Di Qualsiasi Ordine

- Tavola piastra REX con quote, fori, asole, materiali, revisione.
- Lista componenti con rating reali: ponte, condensatori 100 V, buck, diodo ideale, fusibile, cavi, connettori, guardie.
- Calcolo temperatura raddrizzatore/buck a 700 W continuo.
- Procedura test banco e modulo pass/fail.
- Decisione formale su montaggio sotto-telaio: ground clearance, protezione impatti, accesso manutenzione.

## Pacchetto Elettronico

Il pacchetto `hardware/electronics/rex_controller` contiene:

- harness e pinout CSV;
- netlist logica;
- BOM elettronica candidata;
- diagramma funzionale Mermaid;
- grafo potenza DOT;
- progetto KiCad funzionale esportabile;
- harness WireViz rigenerabile;
- note operative per implementazione KiCad/PCB finale.

KiCad CLI 10.0.3, WireViz, Graphviz, OpenSCAD e FreeCAD sono disponibili nella
toolchain locale. Gli output generati restano baseline di review: non sono
ancora ERC/DRC/PCB firmato per produzione.

## Grafici Di Pianificazione

I grafici sotto sono envelope deterministici per pianificare il banco, non
evidenza sperimentale:

- `docs/enterprise/figures/rex_expected_power_current.png`
- `docs/enterprise/figures/rex_expected_rpm_vdc.png`
- `docs/enterprise/figures/rex_expected_thermal.png`
- dataset: `docs/enterprise/datasets/rex_expected_bench_profile.csv`
- script: `scripts/rex_bench_plots.py`

## Fonti Locali

- `Specifiche Range Extender Mulo V2.md`
- `docs/mulo_mk0_range_extender_diy.md`
- `config/rover_params.yaml`
- `src/rover_power/rover_power/energy.py`
- `src/rover_interfaces/msg/RangeExtenderStatus.msg`
- `hardware/firmware/stm32_rex_controller`
- `hardware/electronics/rex_controller`
- `docs/enterprise/range_extender_bench_checklist.md`
