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
- **Controller Safety/Real-Time:** STM32 Nucleo/H7 o equivalente per motori, watchdog, E-stop, ToF anti-caduta, IMU e stop indipendente. Deve implementare il contratto in [Protocollo Safety MCU](../docs/audit/mulo_safety_mcu_protocol.md).
- **Telemetria:** 4G/LTE e/o LoRa per SOS, stato energetico e diagnostica remota.
- **Generatore Ibrido:** Motore ICE con avviamento elettrico e relè a stato solido (SSR).

## 4. Sensori
- **Cella di Carico:** S-Type Load Cell per il verricello (monitoraggio tensione).
- **Encoder:** Encoder assoluto sul tamburo del verricello.
- **Visione:** Camera RGB USB + YOLO/TensorRT su Jetson.
- **LiDAR:** LiDAR 2D DToF economico, es. LDROBOT LD19 o equivalente, montato orizzontale e schermato dal sole.
- **ToF Safety:** Moduli ST VL53L5CX/VL53L1X per vuoti, gradini e zone cieche davanti alle ruote.
- **IMU:** BNO085/BNO086 per prototipo; IMU industriale come upgrade.

## 5. Vano Ricambi e Kit di Manutenzione sul Campo

- **Scatola Vano Ricambi:** Alluminio 5083-H321, 2mm, saldata TIG, IP67 (400×300×120 mm, ~1.8 kg).
- **Fissaggio:** 4x Bulloni M8 a sgancio rapido a leva (Dzus).
- **Antivibrante:** 4x Silent-block neoprene 10 mm.
- **Contenuto Kit (peso totale stimato ~5.7 kg):**
  - Attrezzi: Set brugole M4-M8 (8 pezzi), 6 chiavi a pipa, chiave dinamometrica 10-50 Nm, cacciavite, tronchese, pinza becco lungo, muletto 12V.
  - Ricambi: 1x VESC di riserva, 5x fusibili 30A, 2 set connettori IP68, 1x camera 20x3.0", 1x kit pezze, bulloneria M6/M8 di riserva, 2x chiavetta DIN 6885A, 10x fascette velcro.
  - Emergenza: 1x nastro isolante, 2x bustine stucco epossidico, 1x spray lubrificante, 2 paia guanti antitaglio.
- **Motore di Ricambio (opzionale, stoccaggio separato):** 1x Stepperonline 24V 200W con riduttore 71.5:1 (4.93 kg).

---

## 6. Sistema Verricello Custom (Guinzaglio / Traino Assistito)

Architettura custom: motore StepperOnline BLDC con tamburo in alluminio montato su cuscinetti UCF204 esterni e doppio sistema frenante (elettrofreno custom + Pin-Lock meccanico di sicurezza). Per calcoli completi di dimensionamento, schemi e motivazioni vedere [Sezione 12 di mulo_mk0_hardware_specs.md](../docs/mulo_mk0_hardware_specs.md).

**Carico di progetto:** 1300 N (FS = 1.5 sull'auto-caricamento su rampa 15°)

### 6.1 Componenti Attuazione ed Elettronica

| Componente | Specifica | Peso | Costo stimato |
| :--- | :--- | :--- | :--- |
| **Motore BLDC** | StepperOnline M82B200-24P-30S (24V, 200W nominali, 4200 RPM, poli 10, sensori Hall) | 3.50 kg | €75 |
| **Riduttore Planetario 3 stadi (Conf. A)** | StepperOnline G82-144.5S1 (rapporto 144.5:1, coppia nominale 67.0 Nm, uscita 21 RPM) | 1.43 kg | €45 |
| **Riduttore Planetario 2 stadi (Conf. B)** | StepperOnline G82-56.5S1 (rapporto 56.5:1, coppia nominale 29.0 Nm, uscita 53 RPM) | 1.43 kg | €45 |
| **Elettrofreno Custom (Richiesta)** | Freno elettromagnetico 24V NC (0.8 Nm coppia minima) montato sul retro del motore | 0.35 kg | €35 |

*Nota:* I pesi e i costi finali includono una sola opzione di riduttore.

### 6.2 Componenti Meccanici e Supporto Carico

| Componente | Specifica | Peso | Costo stimato |
| :--- | :--- | :--- | :--- |
| **Cuscinetti Tamburo** | 2x UCF204 flangiati autocentranti (foro 20 mm) imbullonati a telaio per carichi radiali | 1.20 kg | €20 |
| **Tamburo + Asse** | Tamburo custom tornito in Alluminio 6061-T6 (L=80mm) + asse passante in 42CrMo4 | 1.20 kg | €50 |
| **Piastre di Montaggio** | Piastre e staffe di supporto in acciaio S235 spessore 6 mm per telaio anteriore | 0.70 kg | €15 |

### 6.3 Sotto-sistema di Sicurezza Meccanica "Pin-Lock"

| Componente | Specifica | Peso | Costo stimato |
| :--- | :--- | :--- | :--- |
| **Disco di blocco** | Disco in acciaio da 6 mm con 8 fori radiali da 10 mm flangiato sull'albero tamburo | 0.20 kg | €10 |
| **Solenoide a perno** | Solenoide lineare 24V DC normalmente chiuso (perno Ø8 mm in acciaio temprato, molla 25 N) | 0.40 kg | €25 |

### 6.4 Sensoristica

| Componente | Specifica | Peso | Costo stimato |
| :--- | :--- | :--- | :--- |
| **Cella di carico S-Type** | 200 kg, ±0.05% FS, IP67, montata in linea sul cavo | 0.15 kg | €25 |
| **Encoder assoluto tamburo** | Magnetico, 12 bit, SPI/I2C — misura lunghezza cavo estratto | 0.08 kg | €20 |

### 6.5 Cavo e Terminali

| Componente | Specifica | Quantità | Costo stimato |
| :--- | :--- | :--- | :--- |
| **Cavo Dyneema SK75** | Ø4 mm — carico di rottura ≥ 1800 kg | 6 m | €20 |
| **Sleeve protettiva** | Treccia poliestere Ø6 mm (over-braid anti-abrasione a terra) | 2 m | €8 |
| **Cavo emergenza (ricambio)** | Dyneema SK75 Ø4mm — stivato nel vano ricambi | 4 m | €12 |
| **Terminale + Redancia** | Inox 316L pressofuso, redancia Ø10 mm | 1 | €8 |
| **Moschettone HMS** | Certificato UIAA, Ø10 mm, carico rottura 22 kN | 1 | €12 |

### 6.6 Riepilogo Pesi e Costi

| Categoria | Peso | Costo stimato |
| :--- | :--- | :--- |
| Attuazione ed Elettronica (con 1 riduttore + freno custom) | 5.28 kg | €155 |
| Componenti Meccanici e Supporto | 3.10 kg | €85 |
| Sotto-sistema Pin-Lock | 0.60 kg | €35 |
| Cavo + terminali (ricambio incluso) | 0.30 kg | €35 |
| **TOTALE SOTTOSISTEMA VERRICELLO** | **9.28 kg** | **€310** |

> **Nota peso BOM:** L'architettura custom con motore StepperOnline BLDC ridotto porta il sottosistema verricello a **9.28 kg** (+7.08 kg rispetto alla stima iniziale di 2.20 kg). La massa totale del rover aggiornata è **95.06 kg** (Configurazione Ibrida) e **94.68 kg** (Configurazione 100% Elettrica). La variazione è strutturalmente accettabile ed ampiamente entro i limiti di progetto.
