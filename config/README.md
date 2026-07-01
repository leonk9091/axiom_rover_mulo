# Configurazione Rover Mulo

`rover_params.yaml` contiene la baseline comune. I file in `profiles/` sono overlay operativi caricati dal package `rover_bringup`.

## Profili

| Profilo | Uso | Simulazione hardware |
| :--- | :--- | :--- |
| `sim` | Sviluppo senza MCU/VESC reali | Abilitata esplicitamente |
| `bench` | Banco con ruote sollevate | Disabilitata |
| `field` | Test outdoor progressivi | Disabilitata |
| `production` | Configurazione reale completa | Disabilitata |

Comando:

```bash
ros2 launch rover_bringup rover_bringup.launch.py profile:=bench
```

In profili reali la mancanza di seriale MCU o CAN VESC deve generare fault/fallimento, non telemetria simulata.

