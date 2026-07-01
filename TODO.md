# TODO - Aggiornamento Engineering Recommendations

## Piano
- [x] Brainstorm e approvazione piano
- [x] Lettura file esistente
- [x] Aggiungere §6 Digital Twin e Manutenzione Predittiva
- [x] Aggiungere §7 Thermal Management Avanzato
- [x] Aggiungere §8 Comunicazioni Resilienti e Mesh Networking

- [x] Aggiungere §9 Human-Robot Interaction (HRI) e Teleoperazione Immersiva
- [x] Aggiungere §10 Cybersecurity per Robotica Autonoma
- [x] Aggiungere §11 Software Architecture: Micro-ROS, Containerizzazione e CI/CD

- [x] Aggiungere §12 Simulation-Based Validation: SIL/HIL
- [x] Aggiungere §13 Ottimizzazione Strutturale e Materiali Avanzati
- [x] Aggiungere §14 Vibration Monitoring e NVH

- [x] Verifica finale documento

## Integrazione MK0 (UWB Standalone)
- [ ] Cablaggio fisico dei moduli ESP32-S3 e ricetrasmettitori UWB DWM1000
- [ ] Calibrazione della trilaterazione geometrica sul muso del rover (W = 60 cm)
- [ ] Taratura dei sensori laser ToF differenziali (Fascio Basso a 10 cm, Fascio Alto a 25 cm)
- [ ] Test di arrampicata assistita (climbing boost VESC) per ostacoli inferiori a 15 cm
- [ ] Debug dell'inclinometro IMU e della sicurezza anti-ribaltamento a 25 gradi
- [ ] Validazione tracciamento GPS ed esportazione automatica dei file GPX su SD card
- [ ] Implementazione comando operatore Avanza/Stop per procedere lentamente sul percorso GPS registrato
- [ ] Validazione coerenza GPS + odometria + IMU durante avanzamento assistito su traccia

## Protezione Impermeabile — Interventi P0 Consigliati (Bassa Priorità)
- [ ] Aggiungere guarnizione EPDM/silicone al vano batteria per portare il vano da IP54 a IP65 (~€15-30)
- [ ] Installare fori di drenaggio con valvola sul fondo del vano batteria (~€5-10)
- [ ] Installare tappi in silicone per i passacavi IP68 quando il rover non è in ricarica (~€5-10)

> **Nota:** Il pacco batteria è già IP67 e il box elettronico è IP68. L'architettura a livelli multipli è sufficiente per trekking normale. Questi interventi migliorano la protezione del vano (IP54 → IP65) a costo minimo. Vedi [analisi completa](docs/analisi_copertura_impermeabile.md).
