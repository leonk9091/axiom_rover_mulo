# MULO-REX Bench Checklist - Prima Accensione GX50

Data baseline: 2026-06-14

Questa checklist e' un gate P0. Nessun test outdoor e nessun montaggio sul rover
finche' la prova banco non produce evidenza completa.

## Setup Minimo

| Item | Richiesto | Esito |
| :--- | :--- | :--- |
| Banco ventilato | Area esterna o ventilazione forzata con scarico libero | TBD |
| CO monitor | Acceso, testato, visibile all'operatore | TBD |
| Estintore | Classe adatta a combustibili/liquidi/elettrico, entro portata | TBD |
| Fuel leak check | Serbatoio, tubi, tappo e primer senza perdita | TBD |
| Guardie parti rotanti | Cinghia, pulegge, frizione e BLDC coperti | TBD |
| Kill ignition | Verificato con multimetro e prova a motore spento | TBD |
| Throttle spring return | Servo spento = gas minimo | TBD |
| Carico resistivo | Dimensionato per step 100 W -> 700 W | TBD |
| Logging | ROS bag/JSONL + foto setup + manifest | TBD |

## Ordine Prova

1. Alimentare solo STM32 REX via USB/logica.
2. Verificare boot fail-safe: throttle 0, dump off, kill ignition attivo.
3. Inviare comando valido `ice_on=false`: stato `IDLE`, kill rilasciabile solo se safety kill input OK.
4. Simulare `ice_kill=true`: stato `FAULT`, kill ignition attivo.
5. Simulare RPM sopra 7500 o Vdc sopra 70 V con ingressi calibrati: fault e kill.
6. Avviare GX50 senza carico elettrico, throttle minimo, guardie installate.
7. Verificare RPM Hall e nessun contatto/vibrazione anomala.
8. Applicare carico 100 W, poi 300 W, poi 500 W, poi massimo 700 W.
9. Registrare Vdc, corrente carica, temperature ponte/buck/scarico, throttle e fault.
10. Premere E-stop/safety kill: GX50 deve spegnersi o entrare in kill fisico secondo schema.

## Criteri Pass/Fail

| Test | Pass |
| :--- | :--- |
| Kill ignition | Arresto fisico ripetibile da `ice_kill` e safety kill input. |
| RPM | Lettura stabile entro errore accettato dopo taratura. |
| Vdc | Mai oltre 70 V durante spool, no-load e variazioni carico. |
| Corrente | Setpoint raggiunto senza hunting pericoloso o cavi caldi. |
| No-charge fault | Con RPM sopra frizione e corrente zero per 2 s scatta fault. |
| Termico | Ponte, buck e cablaggi restano entro limite scelto con margine. |
| CO/fire | Nessun allarme CO, perdita carburante, plastica/cavo scaldato. |

## Evidence Pack

Salvare:

- `run_manifest.yaml`;
- log JSONL/rosbag;
- foto setup banco e guardie;
- screenshot/grafici Vdc, Icharge, RPM, throttle, temperature;
- commit hash;
- versione firmware STM32 REX;
- decisione finale: pass/fail/anomalia.
