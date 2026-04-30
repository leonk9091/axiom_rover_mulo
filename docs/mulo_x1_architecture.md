# Mulo X-1 Architecture

## Obiettivo
Portare `Mulo` da prototipo ROS 2 a piattaforma R&D da trekking con autonomia condivisa, verricello assistito, supervisione energetica mission-aware e safety separata.

## Domini
- `control`: trazione, telemetria motori, stato rover.
- `mission`: shared autonomy, follow leader, comandi alto livello.
- `terrain`: costo di traversabilità e semantica terreno.
- `power`: SoC/SoH, split batteria-generatore, budget energetico.
- `safety`: watchdog, link supervision, stability margin, E-Stop.
- `winch`: controllo locale tensione e stato verricello.

## Flussi principali
- `mission/leader_vector -> shared_autonomy -> mission/cmd_vel -> vesc_driver`
- `navigation/terrain_type + traction_factor + pitch/roll -> terrain/cost`
- `pitch/roll + tensione + traction + cmd_vel -> safety/stability_margin`
- `stability_margin -> shared_autonomy + winch_manager + safety_watchdog`
- `battery/* + system/power_demand_w + mission/power_mode -> power/energy_budget`

## Compatibilità
- I nodi Python restano validi come reference stack e harness di simulazione.
- Le interfacce `RoverState`, `TerrainCost`, `StabilityMargin`, `EnergyBudget`, `WinchCommand`, `WinchState`, `SafetyState` e `LinkState` sono il nuovo contratto pubblico.
- `shared_autonomy` sostituisce `follow_me` come entrypoint operativo di navigazione trail-first.
