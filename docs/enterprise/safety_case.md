# Safety Case Iniziale - Mulo

## Claim Principale

Il rover puo' essere provato su banco solo se la trazione resta fail-closed: nessun comando software, AI, launch o link radio puo' mantenere coppia motore quando safety MCU, heartbeat, E-stop o consenso motori non sono validi.

## Confini

| Layer | Ruolo safety |
| :--- | :--- |
| E-stop fisico | Stop indipendente da ROS. |
| Safety MCU STM32 Nucleo | Heartbeat, timeout, fault latched, consenso motori, sensori safety locali. |
| VESC | Controllo corrente/RPM e fault driver, subordinato al consenso. |
| Range extender GX50 | Generazione opzionale; mai safety primaria; deve spegnersi su E-stop/fault. |
| ROS/Jetson | Navigazione, logica missione, logging, UI; non e' garante unico dello stop. |
| AI/camera | Semantica e assistenza; non safety primaria. |

## Hazard Iniziali

| Hazard | Mitigazione P0 | Evidenza richiesta |
| :--- | :--- | :--- |
| Movimento inatteso al boot | Motor consent default off | VV-P0-SAFE-001 |
| Host crash con comando attivo | Heartbeat 500 ms | VV-P0-SAFE-002 |
| Frame corrotto o spoofed | CRC obbligatorio command/status | VV-P0-SAFE-004 |
| E-stop software-only | Pulsante NC fisico + relay/opto consenso | VV-P0-SAFE-003 |
| Discesa con batteria piena | Dump load e freni meccanici | VV-P0-ELEC-002, VV-P0-MECH-001 |
| Ribaltamento/pendenza critica | IMU/ToF MCU e limiti velocita' | HIL tilt/drop-off |
| Guasto cablaggio intermittente | Connettori IP, strain relief, wire validation | VV-P0-ELEC-004 |
| GX50 resta acceso dopo stop safety | Kill ignition fail-safe collegato a E-stop/fault | VV-P0-REX-002 |
| Sovraccarica/backfeed da range extender | Fusibile ramo REX, buck CC/CV, diodo ideale, BMS inhibit | VV-P0-REX-004 |
| Rottura cinghia/puleggia/PTO | Guardie e runout/tensionamento prima accensione | VV-P0-REX-003 |
| CO/incendio durante prove REX | Procedura fuel/CO/fire e scarico schermato | VV-P0-REX-005 |

## Safety Requirements

- Safety MCU STM32 Nucleo vince su ROS se gli stati divergono.
- `sentry_static` non puo' accettare movimento lineare.
- `crc16=0` e' ammesso solo in profilo `sim` lato bridge; firmware STM32 finale lo rifiuta.
- Un fault critico e' latched finche' non esiste reset sicuro definito.
- Ogni test outdoor richiede checklist pre-check e post-check.
- Il range extender resta disabilitato in tutti i profili finche' VV-P0-REX-001..005 non sono chiusi.
- Il kill GX50 deve essere indipendente dal solo topic ROS: il topic puo' comandarlo, ma l'evidenza P0 deve dimostrare l'attuatore fisico.

## Stato

Safety case non certificato. E' un pacchetto di evidenze per revisione interna e per impostare un percorso ISO 13849-oriented.
