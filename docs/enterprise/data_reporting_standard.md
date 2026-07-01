# Data and Reporting Standard - Mulo

## Run Manifest

Ogni prova crea `run_manifest.yaml`:

```yaml
run_id: MULO-RUN-YYYYMMDD-HHMM
operator: ""
commit: ""
profile: sim|bench|field|production
hardware_revision: ""
firmware_revision: ""
test_case: ""
environment: bench|indoor|outdoor
mass_kg: null
payload_kg: null
notes: ""
```

## Log Obbligatori

| Canale | Formato | Note |
| :--- | :--- | :--- |
| ROS topics | rosbag2 | Comandi, safety, hardware, power, navigation. |
| MCU events | JSONL/CSV | Ultimi eventi e fault, anche se Jetson fallisce. |
| Test result | Markdown/PDF | Pass/fail, grafici, anomalie e decisione. |
| Photo evidence | JPG/PNG | Cablaggi, setup banco, CAD review quando utile. |

## Topic Minimi

```text
safety/mcu_command
hardware/mcu_status
hardware/state
safety/state
safety/fault_report
motor_telemetry
battery/voltage
battery/current
power/energy_budget
safety/stability_margin
mission/cmd_vel
system/rover_state
range_extender/status
```

## KPI

- stop latency ms;
- max motor current A;
- max bus voltage V;
- min bus voltage V;
- max motor/VESC/battery temperature C;
- heartbeat age ms;
- CRC reject count;
- fault count by source;
- stability margin minimum;
- command vs measured velocity error;
- test pass/fail.

## Campi Range Extender

I test REX devono includere almeno:

- `range_extender.state`;
- `range_extender.fault_code`;
- `range_extender.rpm`;
- `range_extender.dc_link_voltage_v`;
- `range_extender.charge_current_a`;
- `range_extender.generator_power_target_w`;
- `range_extender.throttle_request`;
- `range_extender.engine_kill_request`;
- `battery.voltage_v`;
- `battery.soc`;
- `thermal.rectifier_c`, `thermal.buck_c`, `thermal.exhaust_zone_c` quando disponibili.

## Grafici Rigenerabili REX

Ogni grafico REX deve indicare:

- script generatore;
- dataset sorgente;
- commit;
- profilo configurazione;
- scala sensori ADC usata;
- se il grafico e' envelope pianificato o evidenza reale.

Baseline pianificazione:

| Grafico | Script | Dataset |
| :--- | :--- | :--- |
| `figures/rex_expected_power_current.png` | `scripts/rex_bench_plots.py` | `datasets/rex_expected_bench_profile.csv` |
| `figures/rex_expected_rpm_vdc.png` | `scripts/rex_bench_plots.py` | `datasets/rex_expected_bench_profile.csv` |
| `figures/rex_expected_thermal.png` | `scripts/rex_bench_plots.py` | `datasets/rex_expected_bench_profile.csv` |
