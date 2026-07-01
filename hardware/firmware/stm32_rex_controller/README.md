# STM32 REX Controller Firmware

Firmware di bringup per il controller separato del range extender Honda GX50.

## Ruolo

Questo firmware non sostituisce la safety MCU. La safety MCU resta l'arbitro di
E-stop, consenso motori e fault latched. Il controller REX esegue solo il
controllo locale del generatore:

- valida comandi ausiliari con `aux_crc16`;
- legge RPM, Vdc grezza, corrente carica e temperature;
- comanda throttle e dump-load;
- attiva kill ignition su fault;
- pubblica status JSON verso Jetson/logging.

## Target

- Board default: `nucleo_f446re`
- Board minima candidata: `nucleo_f103rb`
- Board upgrade: `nucleo_h743zi`
- Framework: Arduino STM32 via PlatformIO
- Serial: 115200 bps

## Stati

```text
DISABLED -> IDLE -> SPOOL_UP -> GENERATING
                    \-> FAULT
```

Fail-safe:

- boot: throttle 0, dump-load off, kill ignition active;
- `PIN_SAFETY_KILL_IN` LOW: kill ignition active;
- timeout comandi oltre 500 ms: kill ignition active;
- `ice_kill=true`: kill ignition active;
- RPM > 7500: fault;
- Vdc > 70 V: fault;
- RPM sopra frizione ma corrente carica nulla per 2 s: fault.

## Comando JSON

Il comando e' lo stesso payload ausiliario prodotto da `hardware_bridge`:

```json
{
  "seq": 1,
  "ice_on": true,
  "ice_kill": false,
  "dump_load": false,
  "rex_charge_current_a": 12.0,
  "rex_throttle_request": 0.35,
  "aux_crc16": 12345
}
```

CRC canonico:

```text
seq=<uint32>;ice_on=<0|1>;ice_kill=<0|1>;dump_load=<0|1>;rex_charge_current_a=<%.3f>;rex_throttle_request=<%.3f>
```

## Build

```powershell
pio run -d hardware\firmware\stm32_rex_controller
pio run -d hardware\firmware\stm32_rex_controller -e nucleo_f103rb
```

## Nota Di Taratura

Le scale ADC in `src/main.cpp` sono placeholder di bringup:

- `kVdcScale`;
- `kAcsZeroV`;
- `kAcsSensitivityVA`;
- conversione NTC temperature.

Non usare il banco GX50 reale finche' queste costanti non sono misurate e
registrate in un evidence pack.
