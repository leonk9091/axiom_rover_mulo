# Cybersecurity Plan - Mulo

## Regola

Cybersecurity diventa P0 prima di telemetria remota reale o comando remoto oltre il banco. Finche' il rover e' in test locale, il focus resta safety fail-closed.

## Threat Model Iniziale

| Threat | Rischio | Mitigazione |
| :--- | :--- | :--- |
| Topic spoofing ROS 2 | Comando moto non autorizzato | SROS2/DDS security e allowlist topic. |
| Firmware non firmato | Update malevolo o errato | Firmware signing e hash release. |
| Wi-Fi/4G esposti | Accesso remoto non controllato | Network zoning e VPN/manutenzione separata. |
| CAN injection | Comandi/fault falsi VESC | Segmentazione, gateway e monitor bus. |
| Log tampering | Evidenza non affidabile | Manifest con commit, checksum e timestamp. |

## Deliverable

- STRIDE table per ROS, MCU, CAN, telemetria e update.
- SROS2 policy: chi pubblica/sottoscrive `cmd_vel`, `safety/estop`, `hardware/*`.
- Key management: generazione, rotazione, revoca.
- SBOM software/firmware/container.
- Incident playbook: isolare rete, disabilitare trazione, esportare log, ripristinare release nota.

