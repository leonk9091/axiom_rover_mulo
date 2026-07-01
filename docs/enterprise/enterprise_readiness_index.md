# Enterprise Readiness Index - Mulo

Data baseline: 2026-06-14

Questo indice raccoglie gli artefatti minimi per portare il rover Mulo da prototipo avanzato a progetto verificabile, ordinabile e manutenibile. Hardware fisico e ordini restano bloccati finche' i P0 non hanno evidenza.

## Artefatti

| Area | File | Uso |
| :--- | :--- | :--- |
| Requisiti | `system_requirements.md` | Baseline `MULO-SYS-###` con acceptance criteria. |
| Tracciabilita' | `traceability_matrix.csv` | Collegamento requisito, design, test, evidenza, BOM e rischio. |
| V&V | `vv_master_plan.md` | Piano test unit, integration, SIL, HIL, banco e campo. |
| Safety | `safety_case.md` | Safety case iniziale ISO 13849-oriented. |
| Elettrico | `electrical_baseline_24v.md` | Baseline bus 24 V, potenza, CAN, protezioni e ground. |
| Cablaggio | `wiring_validation_matrix.csv` | Wire list minima e criteri di validazione. |
| Produzione | `manufacturing_readiness_package.md` | Tavole, CAD, QC incoming, assembly e fine linea. |
| Dati | `data_reporting_standard.md` | Log, rosbag, JSONL, KPI e report prove. |
| Range extender | `range_extender_readiness.md` | Task, gate e interfacce per il sottosistema Honda GX50. |
| REX validation | `range_extender_validation_matrix.csv` | Test P0/P1 per GX50, carica 24 V, parti rotanti e fuel/CO/fire. |
| REX bench | `range_extender_bench_checklist.md` | Checklist operativa prima accensione e evidence pack GX50. |
| REX electronics | `../../hardware/electronics/rex_controller` | Netlist, harness, BOM e note KiCad per carrier STM32 REX. |
| Digital twin | `digital_twin_scenarios.md` | Scenari SIL/HIL ripetibili. |
| Cybersecurity | `cybersecurity_plan.md` | Threat model, SROS2, chiavi, update e recovery. |
| BOM | `mulo_bom_candidate_shortlist.csv` | Shortlist candidati da validare prima dell'acquisto. |
| Safety MCU | `../../hardware/firmware/stm32_safety_mcu/stm32_nucleo_safety_pinout.md` | Pinout logico per NUCLEO-F446RE/F103RB e regole fail-safe. |
| REX firmware | `../../hardware/firmware/stm32_rex_controller` | Firmware STM32 separato per controllo Honda GX50 e kill ignition. |

## Regola Gate

Un item P0 passa da `Da chiudere` a `Chiuso` solo se ha:

1. requisito numerato;
2. design o interfaccia versionata;
3. test case con pass/fail;
4. evidenza archiviata;
5. rischio residuo accettato.
