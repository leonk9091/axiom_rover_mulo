## 1. Struttura (Acciaio)
- **Profilo:** Tubolare Quadro Acciaio S235, 30x30x2mm (2 barre da 2m).
- **Controventature:** Piatto d'acciaio 20x3mm per rinforzo diagonale moduli.
- **Giunti:** Piastre a L in acciaio per giunti "Bolt-Through".
- **Bulloneria:** Bulloni M8 Classe 8.8, dadi autobloccanti (Nyloc).
- **Snodo Centrale:** 2x Cuscinetti a ritta UCP204 + Albero 20mm + Piastra rinforzo 6mm.

## 2. Drivetrain (4WD Reinforced)
- **Motori:** 4x Stepperonline 24V 200W (71.5:1).
- **Cuscinetti Esterni:** 4x Cuscinetti flangiati UCF204 (Ø 20mm).
- **Alberi Custom:** 4x Alberi di prolunga in 42CrMo4 (Tornitura custom).
- **Ruote:** 4x Ruote ANTERIORI Cargo E-bike da 20" (Mozzo 33-36mm, 6 fori).
- **Freni:** 4x Pinze Avid BB7 + Dischi 203mm + Leve a cricchetto.

## 3. Alimentazione e Controllo
- **Batteria:** Pacco LiFePO4 24V (Capacità suggerita: >30Ah).
- **Cervello AI:** Jetson Orin Nano Super 8GB come base; Jetson Orin NX 16GB come upgrade se la percezione AI diventa il collo di bottiglia.
- **Controller Safety/Real-Time:** STM32 Nucleo/H7 o equivalente per motori, watchdog, E-stop, ToF anti-caduta, IMU e stop indipendente.
- **Telemetria:** 4G/LTE e/o LoRa per SOS, stato energetico e diagnostica remota.
- **Generatore Ibrido:** Motore ICE con avviamento elettrico e relè a stato solido (SSR).

## 4. Sensori
- **Cella di Carico:** S-Type Load Cell per il verricello (monitoraggio tensione).
- **Encoder:** Encoder assoluto sul tamburo del verricello.
- **Visione:** Camera RGB USB + YOLO/TensorRT su Jetson.
- **LiDAR:** LiDAR 2D DToF economico, es. LDROBOT LD19 o equivalente, montato orizzontale e schermato dal sole.
- **ToF Safety:** Moduli ST VL53L5CX/VL53L1X per vuoti, gradini e zone cieche davanti alle ruote.
- **IMU:** BNO085/BNO086 per prototipo; IMU industriale come upgrade.
