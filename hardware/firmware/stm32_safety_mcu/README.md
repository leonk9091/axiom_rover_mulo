# STM32 Safety MCU Firmware

Firmware di bringup per la safety MCU STM32 Nucleo del rover Mulo.

Questo progetto implementa il contratto definito in:

`docs/audit/mulo_safety_mcu_protocol.md`

## Target

- Board default: `nucleo_f446re`
- Board minima candidata: `nucleo_f103rb`
- Board upgrade: `nucleo_h743zi`
- Framework: Arduino STM32 via PlatformIO
- Serial: 115200 bps
- Command input: JSON lines da `hardware_bridge`
- Status output: JSON lines verso `hardware_bridge`

## Safety Policy Minima

- `PIN_MOTOR_CONSENT` parte sempre disabilitato.
- E-stop fisico NC su `PIN_ESTOP_NC`: LOW/open -> fault latched e consenso off.
- `estop_request=true` dal comando Jetson -> fault latched e consenso off.
- Timeout comando: massimo 500 ms -> consenso off.
- CRC comando: `crc16` e' obbligatorio e viene verificato con CRC-16/CCITT-FALSE sulla stringa canonica del protocollo.

## Bringup

1. Collegare solo USB seriale e alimentazione logica.
2. Verificare che `PIN_MOTOR_CONSENT` resti LOW al boot.
3. Inviare un comando valido con `enable_motors_request=false`.
4. Inviare un comando valido con `enable_motors_request=true` e E-stop rilasciato.
5. Interrompere i comandi: il consenso deve tornare LOW entro 500 ms.
6. Premere E-stop: il consenso deve andare LOW e restare latched.

## Comandi

Esempio:

```json
{"seq":1,"stamp_ms":1000,"mode":"manual","desired_linear_velocity_ms":0.0,"desired_angular_velocity_rads":0.0,"timeout_ms":250,"estop_request":false,"enable_motors_request":false,"max_current_a":18.0,"crc16":12345}
```

`crc16=0` viene rifiutato anche in bringup: i test devono generare frame completi usando la stessa stringa canonica del bridge ROS.
