# Pinout Logico Safety MCU - STM32 Nucleo

Target safety finale: STM32 Nucleo, non ESP32.

## Board Candidate

| Board | Ruolo | Nota |
| :--- | :--- | :--- |
| NUCLEO-F446RE | Preferita per MK0/X-1 safety | Cortex-M4/FPU, buon margine per CRC, IMU, ToF, CAN e logging compatto. |
| NUCLEO-F103RB | Candidata minima | Sufficiente per heartbeat, E-stop, consenso motori e I/O base; meno margine per crescita futura. |
| NUCLEO-H7 family | Upgrade | Utile se crescono HIL, logging e sensori locali; non obbligatoria per prima safety board. |

`NUCLEO-F443RE` non e' trattata come baseline perche' non risulta una board Nucleo ST ufficiale verificata nel catalogo consultato; se il codice era un refuso, usare `NUCLEO-F446RE`.

## Pinout Logico

I pin fisici vanno assegnati dopo scelta board e carrier, ma queste funzioni sono obbligatorie:

| Funzione | Direzione | Fail-safe | Requisito |
| :--- | :--- | :--- | :--- |
| E-stop NC | Input | Aperto/LOW = stop | Non dipende da ROS. |
| Motor consent / STO | Output | LOW/open = motori disabilitati | Default off a boot/reset. |
| Dump load enable | Output | Off in boot/fault | Attivo solo da policy energia validata. |
| Jetson link | UART o CAN | Timeout = stop | CRC, seq e timeout <= 500 ms. |
| VESC CAN | CAN | Lost = stop/degraded | Telemetria fault essenziale. |
| IMU safety | I2C/SPI/UART | Stale = degraded/stop | Vicina al baricentro. |
| ToF safety | I2C/UART | Stale = degraded/stop | Vuoti, gradini, frontale ruote. |
| Current/voltage sense | ADC/CAN/UART | Invalid = degraded/stop | Usata per overcurrent/brownout. |

## Regola

L'ESP32 puo' restare come prototipo o modulo ausiliario non safety-critical, ma il consenso motori finale deve passare dalla safety MCU STM32.

