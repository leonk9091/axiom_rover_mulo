# Protocollo Safety MCU - Jetson/ROS 2 verso STM32

Data: 2026-06-12

Questo documento congela il contratto minimo tra il computer alto livello
Jetson/ROS 2 e la MCU safety real-time del Mulo. La baseline safety e'
STM32 Nucleo, con NUCLEO-F446RE come candidato preferito e NUCLEO-F103RB come
minimo verificabile.

Obiettivo: la Jetson puo' proporre movimento e modalita' missione, ma la MCU
deve poter togliere consenso ai motori senza aspettare ROS 2 quando heartbeat,
comando, E-stop, sensori locali o potenza diventano non affidabili.

## 1. Confini di Responsabilita'

| Livello | Responsabilita' | Non deve fare |
| :--- | :--- | :--- |
| Jetson / ROS 2 | Percezione, Nav2/shared autonomy, follow-me, logging completo, UI, mission logic. | Essere l'unico garante dello stop motori. |
| Safety MCU STM32 | Heartbeat, timeout comandi, E-stop, consenso motori, lettura sensori safety locali, fault latched, stato compatto verso ROS. | Prendere decisioni globali basate su AI, GPS o mappe. |
| VESC / Potenza | Controllo corrente/RPM, telemetria, fault driver, frenata elettrica. | Restare abilitati se manca consenso safety. |

La regola di progetto e': se Jetson e MCU non sono d'accordo, vince la MCU.

## 2. Collegamenti Minimi

| Collegamento | Direzione | Mezzo consigliato | Requisito |
| :--- | :--- | :--- | :--- |
| Comandi moto | Jetson -> MCU | UART robusta o CAN | CRC, sequence number, timeout esplicito. |
| Stato safety | MCU -> Jetson | UART robusta o CAN | Pubblicato almeno a 20 Hz. |
| Consenso motori | MCU -> circuito potenza/VESC | GPIO fail-safe isolato | Default fisico = trazione disabilitata. |
| E-stop fisico | Pulsante -> MCU/circuito | NC cablato | Non dipende da ROS 2. |
| ToF/IMU safety | Sensori -> MCU | I2C/SPI/UART locale | Soglie conservative lato MCU. |
| Fault VESC essenziali | VESC -> MCU o Jetson+MCU | CAN preferibile | Perdita CAN o fault critico porta stop/degraded. |
| Comandi ausiliari REX/dump | Jetson -> MCU/ECU REX | UART robusta o CAN | CRC ausiliario dedicato, fail-off, kill prioritario. |

Per il prototipo iniziale la seriale JSON e' accettabile. Per il rover finale,
il frame deve avere almeno `seq`, `crc`, `timeout_ms` e schema stabile.

## 3. Comando Jetson -> MCU

Frequenza nominale: 20 Hz. Frequenza minima valida: 10 Hz.

Timeout massimo accettato: 500 ms. Il valore `timeout_ms` nel frame non puo'
superare 500 ms; se arriva maggiore, la MCU lo clampa a 500 ms o rifiuta il
comando.

| Campo | Tipo | Unita' | Range | Note |
| :--- | :--- | :--- | :--- | :--- |
| `seq` | uint32 | - | monotono | Incrementa a ogni frame valido. |
| `stamp_ms` | uint32 | ms | monotono | Timestamp lato Jetson, usato solo per log. |
| `mode` | enum | - | vedi sezione 5 | Modalita' richiesta, non autoritativa. |
| `desired_linear_velocity_ms` | float32 | m/s | -1.2..1.2 | La MCU applica limiti locali piu' severi se serve. |
| `desired_angular_velocity_rads` | float32 | rad/s | -1.5..1.5 | Comando yaw/skid-steer. |
| `timeout_ms` | uint16 | ms | 50..500 | Scadenza comando. |
| `estop_request` | bool | - | true/false | True attiva fault latched. |
| `enable_motors_request` | bool | - | true/false | Richiesta, valida solo se safety OK. |
| `max_current_a` | float32 | A | 0..30 | Limite superiore richiesto; MCU puo' ridurre. |
| `crc16` | uint16 | - | CCITT-FALSE | Calcolato su tutto il frame escluso CRC. |

Il CRC del comando non viene calcolato sul JSON grezzo. Per evitare differenze
di serializzazione tra Python e firmware, si calcola su questa stringa
canonica ASCII a campi fissi:

```text
seq=<uint32>;stamp_ms=<uint32>;mode=<string>;desired_linear_velocity_ms=<%.3f>;desired_angular_velocity_rads=<%.3f>;timeout_ms=<uint16>;estop_request=<0|1>;enable_motors_request=<0|1>;max_current_a=<%.3f>
```

Esempio JSON prototipo:

```json
{
  "seq": 42,
  "stamp_ms": 123456,
  "mode": "trek_follow",
  "desired_linear_velocity_ms": 0.35,
  "desired_angular_velocity_rads": -0.12,
  "timeout_ms": 250,
  "estop_request": false,
  "enable_motors_request": true,
  "max_current_a": 18.0,
  "crc16": 53191
}
```

### 3.1 Comandi Ausiliari REX e Dump Load

I comandi non-traction, come range extender Honda GX50 e dump load, non devono
viaggiare come booleani non protetti. Per compatibilita' con il CRC trazione,
il bridge aggiunge un CRC ausiliario separato `aux_crc16` calcolato su:

```text
seq=<uint32>;ice_on=<0|1>;ice_kill=<0|1>;dump_load=<0|1>;rex_charge_current_a=<%.3f>;rex_throttle_request=<%.3f>
```

Regole:

- `ice_kill=true` vince sempre su `ice_on=true`;
- se `aux_crc16` manca o non torna in profilo reale, ECU/MCU deve ignorare i comandi ausiliari e lasciare REX spento;
- il kill ignition GX50 deve essere attuabile anche da fault MCU/E-stop senza aspettare ROS;
- `rex_charge_current_a` e `rex_throttle_request` sono richieste, non consenso safety.

## 4. Stato MCU -> Jetson

Frequenza nominale: 20 Hz. Deve continuare anche in fault, se la MCU e'
alimentata.

| Campo | Tipo | Unita' | Note |
| :--- | :--- | :--- | :--- |
| `seq_ack` | uint32 | - | Ultimo comando valido accettato. |
| `mcu_uptime_ms` | uint32 | ms | Tempo da boot MCU. |
| `safety_state` | enum | - | `boot`, `safe_disabled`, `armed`, `degraded`, `estop`, `fault`. |
| `estop_active` | bool | - | Include E-stop fisico e richieste software latched. |
| `motor_consent` | bool | - | Stato reale linea consenso motori. |
| `fault_code` | enum/string | - | Un fault principale, con priorita' critica. |
| `fault_latched` | bool | - | Richiede reset fisico o sequenza sicura. |
| `heartbeat_age_ms` | uint16 | ms | Eta' ultimo comando valido Jetson. |
| `sensor_validity` | bitmask | - | IMU, ToF, encoder, VESC, tensione, corrente. |
| `degraded_mode` | enum | - | `none`, `command_only`, `low_speed`, `link_loss_hold`, `limp_home`. |
| `roll_rad` | float32 | rad | Assetto locale MCU. |
| `pitch_rad` | float32 | rad | Assetto locale MCU. |
| `battery_voltage_v` | float32 | V | Se disponibile localmente. |
| `motor_current_a` | float32 | A | Totale o massimo misurato. |
| `crc16` | uint16 | - | Calcolato su frame escluso CRC. |

Esempio JSON prototipo:

```json
{
  "seq_ack": 42,
  "mcu_uptime_ms": 124010,
  "safety_state": "armed",
  "estop_active": false,
  "motor_consent": true,
  "fault_code": "none",
  "fault_latched": false,
  "heartbeat_age_ms": 36,
  "sensor_validity": 31,
  "degraded_mode": "none",
  "roll_rad": 0.03,
  "pitch_rad": -0.08,
  "battery_voltage_v": 25.8,
  "motor_current_a": 4.2,
  "crc16": 48220
}
```

## 5. Stati e Transizioni

| Stato | Descrizione | Consenso motori |
| :--- | :--- | :--- |
| `boot` | MCU appena avviata, self-test in corso. | Off |
| `safe_disabled` | Nessun fault critico, ma motori non armati. | Off |
| `armed` | Comando valido, E-stop rilasciato, sensori minimi validi. | On |
| `degraded` | Movimento limitato per sensore/link non critico o 3WD. | On limitato |
| `estop` | E-stop fisico/software attivo. | Off latched |
| `fault` | Fault critico non E-stop: heartbeat, pendenza, corrente, CAN. | Off latched o off fino a recovery |

Modalita' missione accettate:

```text
manual
trek_follow
advance_trace
shared_autonomy
sentry_static
recovery
```

La MCU rifiuta movimento lineare in `sentry_static`. In sentry sono ammessi
solo comandi yaw lenti se freni, assetto e sensori risultano sicuri.

## 6. Fault Minimi

| Codice | Trigger | Azione MCU |
| :--- | :--- | :--- |
| `heartbeat_timeout` | Nessun comando valido entro `timeout_ms` o 500 ms. | Velocita' zero, consenso off se comando era attivo. |
| `crc_error` | Frame non valido ripetuto. | Ignora frame; fault se consecutivo oltre soglia. |
| `estop_physical` | Pulsante NC aperto/premuto. | Consenso off latched. |
| `estop_software` | `estop_request=true`. | Consenso off latched. |
| `imu_stale` | IMU non aggiornata oltre soglia. | Stop o degraded secondo modalita'. |
| `tilt_critical` | Roll/pitch oltre soglia. | Stop immediato. |
| `tof_dropoff` | Vuoto/gradino critico davanti ruote. | Stop immediato. |
| `motor_overcurrent` | Corrente persistente oltre limite. | Recovery breve, poi stop latched. |
| `vesc_can_lost` | Perdita VESC critico. | Stop o `limp_home` se configurato. |
| `brownout` | Tensione logica/potenza sotto soglia. | Consenso off. |
| `rex_overspeed` | GX50/BLDC oltre limite RPM. | Kill ignition, generazione off, fault latched. |
| `rex_dc_link_ovp` | DC link REX oltre soglia. | Kill ignition, dump/load policy safe, fault latched. |
| `rex_no_charge_current` | Gas aperto ma corrente carica nulla oltre timeout. | Kill ignition e diagnosi alternatore/buck/cinghia. |

## 7. Log Minimo MCU

La MCU deve mantenere almeno un ring buffer degli ultimi 256 eventi; se e'
presente SD/flash esterna, log persistente CSV/JSONL.

Campi evento:

```text
uptime_ms
event_type
fault_code
safety_state
mode
seq_ack
heartbeat_age_ms
motor_consent
battery_voltage_v
motor_current_a
roll_rad
pitch_rad
```

## 8. Pinout Logico Minimo

| Funzione | Direzione | Stato fail-safe |
| :--- | :--- | :--- |
| E-stop NC | Input | Aperto = stop |
| Motor consent / STO | Output | Low/open = motori disabilitati |
| Dump load enable | Output | Off se MCU in boot/fault, on solo da policy energia |
| IMU safety | Input bus | Stale = degraded/stop |
| ToF frontali | Input bus | Stale = degraded/stop |
| VESC CAN | Bus | Lost = stop/degraded |
| Jetson link | UART/CAN | Lost = stop |

Usare pull-up/pull-down fisici per garantire che durante boot/reset MCU il
consenso motori resti disabilitato.

## 9. Test di Accettazione Banco

| Test | Metodo | Pass/fail |
| :--- | :--- | :--- |
| Boot sicuro | Alimentare MCU con VESC collegati ma ruote sollevate. | `motor_consent=false` fino ad arm esplicito. |
| Heartbeat perso | Inviare comando moto, poi fermare Jetson/bridge. | Motori a zero entro 500 ms. |
| E-stop fisico | Premere fungo durante comando attivo. | Consenso off immediato, fault latched. |
| CRC errato | Inviare 10 frame corrotti. | Nessun comando accettato; fault diagnostico. |
| IMU stale | Disconnettere o bloccare IMU. | Stop/degraded secondo policy, log evento. |
| Tilt critico | Simulare roll/pitch oltre soglia. | Stop immediato. |
| ToF vuoto | Simulare drop-off davanti ruote. | Stop immediato. |
| Reboot Jetson | Riavviare Jetson durante moto. | MCU stoppa e resta safe fino a comandi validi. |
| Reboot MCU | Resettare MCU con VESC alimentati. | Linea consenso resta fisicamente off. |
| Fault REX | Simulare overspeed/Vdc alta/no-current. | `range_extender/status` fault, kill ignition e E-stop safety. |

## 10. Impatto sul Workspace ROS 2

Il nodo `hardware_bridge` deve diventare il traduttore tra topic ROS 2 e
protocollo MCU:

- sottoscrive comando alto livello (`mission/cmd_vel` o topic dedicato safety command);
- invia frame command con `seq`, velocita', mode, `timeout_ms`, CRC;
- pubblica il comando osservabile su `safety/mcu_command`;
- pubblica lo stato compatto MCU su `hardware/mcu_status`;
- pubblica `hardware/state`, `safety/state`, `safety/fault_report`;
- non considera valido il sistema se `heartbeat_age_ms` o `seq_ack` non sono coerenti.

Per la fase attuale si puo' mantenere una seriale JSON di bringup, ma ogni
campo sopra deve essere mappabile al firmware STM32 finale.

Lo scaffold iniziale del firmware STM32/H7 si trova in
`hardware/firmware/stm32_safety_mcu`.
