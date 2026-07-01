# Final Assembly Readiness - MULO MK0/REX

Data baseline: 2026-06-14

Questo file e' l'indice operativo per passare da prototipo/documentazione a
pacchetto professionale di assemblaggio. Hardware fisico e ordini restano in
pausa finche' i gate P0 non sono chiusi con evidenza.

## Pacchetto Generabile

| Pacchetto | Sorgente | Output atteso |
| :--- | :--- | :--- |
| Toolchain | `docs/enterprise/toolchain_manifest.md` | elenco versioni e percorsi CLI |
| Schematic REX | `hardware/electronics/rex_controller/kicad/mulo_rex_controller` | PDF/SVG/ERC KiCad |
| Cablaggio REX | `hardware/electronics/rex_controller/wireviz/rex_controller_harness.yml` | HTML/PNG/SVG/TSV WireViz |
| Architettura potenza REX | `hardware/electronics/rex_controller/rex_power_architecture.dot` | PNG/SVG/PDF Graphviz |
| Piastra controller REX | `hardware/mechanical/rex_controller_carrier` | STL/DXF/STEP/FCStd |
| Dati banco REX | `scripts/rex_bench_plots.py` | CSV + grafici envelope |
| Evidence pack | `reports/evidence` | manifest, template report e cartelle test |

## Gate P0 Prima Di Assemblaggio Finale

| Gate | Stato | Criterio di chiusura |
| :--- | :--- | :--- |
| Baseline elettrica 24 V | aperto | schema potenza, fusibili, sezionatore, dump load e masse firmati |
| REX disabilitato di default | chiuso software | tutti i profili hanno `range_extender_enabled: false` |
| Harness REX rigenerabile | avviato | WireViz generato e wire list con sezioni/rating finali |
| KiCad REX | avviato | schematic capture completo con ERC pulito e review connettori |
| Meccanica REX | avviato | piastra/guardie in CAD, quote, tolleranze, STEP/DXF e controllo interferenze |
| Evidence pack | avviato | ogni VV ha manifest, log, report, foto e approvazione |
| ROS/STM32 REX end-to-end | aperto | bridge seriale reale con parser status, CRC, timeout e fault injection |
| Firmware HIL | aperto | build, simulazione fault e test su Nucleo con I/O reali |

## Sequenza Di Assemblaggio Raccomandata

1. Congelare BOM P0 con rating reali e candidati acquistabili.
2. Generare gli artefatti con `scripts/generate_assembly_artifacts.ps1`.
3. Fare review documentale: requisiti, safety case, V&V, schemi, harness, piastra.
4. Costruire banco a bassa energia: solo logica 5 V/USB, nessun GX50 acceso.
5. Validare kill ignition a motore spento e consenso safety fail-closed.
6. Validare sensori RPM/Vdc/Icharge/temp con simulatori o alimentatori limitati.
7. Solo dopo: prova REX senza carica batteria, con guardie, CO monitor e fuel/fire checklist.
8. Solo dopo: carica su carico resistivo e poi integrazione batteria con BMS/diodo ideale.

## Cosa Non E' Ancora Autorizzato

- Ordine di lavorazioni custom telaio/REX senza tavole quotate.
- Test outdoor con REX acceso.
- Collegamento diretto DC link/batteria senza protezione e dump/load plan.
- Movimento rover in profilo reale se MCU/VESC/safety non sono validi.
- Considerare i documenti storici ESP32 come baseline safety finale.
