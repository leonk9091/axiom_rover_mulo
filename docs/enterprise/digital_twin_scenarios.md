# Digital Twin and SIL/HIL Scenarios - Mulo

## Obiettivo

Il digital twin deve servire a riprodurre fault e condizioni limite prima del terreno. Non sostituisce il test fisico, ma impedisce di scoprire per la prima volta un failure mode con il rover libero.

## Scenari Minimi

| ID | Scenario | Input | Expected |
| :--- | :--- | :--- | :--- |
| SIL-001 | Heartbeat loss | Comando moto poi stop bridge | `mission/cmd_vel=0`, fault heartbeat. |
| SIL-002 | E-stop | Topic e/o input simulato | Stato estop latched. |
| SIL-003 | Tilt critical | Roll/pitch oltre soglia | Stop safety. |
| SIL-004 | Drop-off ToF | Vuoto davanti ruote | Stop safety. |
| SIL-005 | UWB loss | Leader invisibile o incoerente | `search_hold` o stop. |
| SIL-006 | VESC fault | Fault code o CAN lost | Stop/degraded. |
| SIL-007 | High SOC descent | Rigenerazione con batteria alta | Dump load command e bus limitato. |
| SIL-008 | Stallo | Corrente alta e velocita' nulla | Recovery breve poi stop. |
| SIL-009 | REX disabled gate | Power demand alto con `range_extender_enabled=false` | `RangeExtenderStatus=DISABLED`, nessun start GX50. |
| SIL-010 | REX overvoltage | `range_extender/dc_link_voltage > 70 V` | `engine_kill_request=true`, fault critico, E-stop safety. |
| SIL-011 | REX overspeed | `range_extender/rpm > 7500` | Kill ignition richiesto e fault latched. |
| SIL-012 | REX no-charge | Throttle alto, RPM valido, corrente carica zero | Fault `NO_CHARGE_CURRENT` e diagnosi cinghia/buck/alternatore. |
| SIL-013 | REX high SOC | SoC > soglia stop | Generazione disabilitata, nessuna carica batteria. |

## Deliverable

- Launch dedicato sim.
- World/scenario file versionato.
- Script fault injection.
- Rosbag golden per regressioni.
- Report automatico KPI.
- Fault injection REX per RPM, Vdc, corrente carica e thermal headroom.
