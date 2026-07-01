# BOM — Range Extender DIY "Mulo" — Rev. 1.0 (da acquistare)

**Stato:** PRONTO PER ACQUISTO
**Data:** 2026-06-30
**Progetto:** Axiom Rover Mulo MK0 — Sottosistema generatore ibrido stazionario off-road

---

## 1. GRUPPO TERMICO (Motore + Trasmissione + PTO)

| # | Componente | Specifica Esatta | Qt. | Costo Est. | Note / Dove comprare |
|:--|:-----------|:-----------------|:----|:----------:|:---------------------|
| 1.1 | **Motore Honda GX50** | 47.9cc, 1.47 kW, carburatore a membrana Walbro, avviamento a strappo | 1 | ~200-250 EUR | Rivenditore Honda ufficiale IT / eBay. **NON GX35** (meno potenza). |
| 1.2 | **Frizione centrifuga 9T per GX50** | Campana frizione femmina scanalata **9 denti (9T)**, con carter + cuscinetti integrati, compatibile GX50 76mm | 1 | ~15-25 EUR | AliExpress "9 tooth clutch drum GX50" / ricambi decespugliatore |
| 1.3 | **Albero millerighe 9T** | Asta acciaio diam. 8mm, terminale scanalato **9 denti**, tagliare a ~15 cm | 1 | ~5-10 EUR | Ricambi decespugliatore / agraria |
| 1.4 | **Cuscinetto flangiato autoallineante KP08** | Flangia KP08, foro interno diam. 8mm, sede sferica interna autoallineante | 1 | ~8-12 EUR | AliExpress "KP08 bearing" / distributori SKF |
| 1.5 | **Puleggia HTD 5M foro 8mm** (lato GX50) | HTD 5M, **20 denti**, larghezza 15mm, foro **8mm** | 1 | ~8-12 EUR | AliExpress "HTD 5M 20T 8mm pulley" |
| 1.6 | **Puleggia HTD 5M foro 12mm** (lato BLDC) | HTD 5M, **20 denti**, larghezza 15mm, foro **12mm** con chiavetta | 1 | ~8-12 EUR | AliExpress "HTD 5M 20T 12mm pulley keyway" |
| 1.7 | **Cinghia HTD 5M 15mm** | Passo 5M, larghezza **15mm**, lunghezza ~300-400mm (misurare dopo montaggio). **Comprarne 2** (una di scorta) | 2 | ~8-15 EUR | AliExpress "HTD 5M 15mm belt" / RS Components / Mectral |
| 1.8 | **Spina elastica (Roll Pin)** | Acciaio, diam. **3 o 4mm**, lunghezza 20-25mm | 1 pack | ~2 EUR | Ferramenta |
| 1.9 | **Bloccante coassiale anaerobico** | **Loctite 638** o **Loctite 648** ORIGINALE Henkel. Alt. italiana: **Loxeal 83-21** o **Arexons PRO 52A43** | 1 flacone | ~12-18 EUR | Utensileria / Amazon IT (verificare QR Henkel) |

**Subtotale: ~266-356 EUR**

---

## 2. ALTERNATORE (BLDC Outrunner)

| # | Componente | Specifica Esatta | Qt. | Costo Est. | Note |
|:--|:-----------|:-----------------|:----|:----------:|:-----|
| 2.1 | **BLDC Outrunner 80100 Kv120-170** | Statore diam. 80mm, lunghezza 100mm, **Kv 120-170**, trifase, albero **diam. 12mm + chiavetta**, corrente nominale >= 40A | 1 | ~80-120 EUR | AliExpress "80100 BLDC Kv120" / APS 80100 / Turnigy RotoMax 80cc |

Kv target 120-150: a 6500 RPM -> ~48-50V AC -> ~52-55V DC grezza -> Buck regola a 28.8V.
Verificare albero 12mm con sede chiavetta prima dell'acquisto.

**Subtotale: ~80-120 EUR**

---

## 3. ELETTRONICA DI POTENZA

| # | Componente | Specifica Esatta | Qt. | Costo Est. | Note |
|:--|:-----------|:-----------------|:----|:----------:|:-----|
| 3.1 | **Ponte raddrizzatore trifase SQL100A** | 6 diodi trifase, **100A / 100V**, su dissipatore obbligatorio | 1 | ~8-15 EUR | AliExpress "SQL100A rectifier bridge" / Mouser |
| 3.2 | **Dissipatore alluminio per SQL100A** | Superficie minima 100 cm2, boccola centrale | 1 | ~5-10 EUR | AliExpress "heatsink SQL100A" |
| 3.3 | **Condensatori 100V 4700uF** | Elettrolitici, **105 gradi C**, marca Nichicon/Rubycon/Panasonic/EPCOS. 2 in parallelo + 1 scorta | 3 | ~8-15 EUR | Mouser / Farnell. NO generici sconosciuti. |
| 3.4 | **Regolatore Buck CC/CV 1500W** | Input 15-90V DC, trimmer separati **CC** e **CV**, output tarare a 28.8V / 20A | 1 | ~40-55 EUR | AliExpress "1500W buck CC CV" / DROK / JUNTEK |
| 3.5 | **Modulo Diodo Ideale 50A / 80V** | MOSFET ideal diode, impedisce reflusso verso generatore a motore spento | 1 | ~10-18 EUR | AliExpress "ideal diode module 50A 80V" |
| 3.6 | **Fusibile 60A DC + portafusibile** | Fusibile a lama 60A / 80V DC, portafusibile impermeabile | 1 | ~5-8 EUR | Ferramenta auto / elettronica |

**Subtotale: ~76-121 EUR**

---

## 4. MICRO-ECU STM32 (Centralina REX)

| # | Componente | Specifica Esatta | Qt. | Costo Est. | Note |
|:--|:-----------|:-----------------|:----|:----------:|:-----|
| 4.1 | **STM32 Nucleo-F446RE** | Ufficiale ST, 180 MHz, timer hardware Input Capture, ADC multi-canale, UART/CAN/PWM | 1 | ~15-20 EUR | Mouser / Farnell / RS Components. Solo ufficiale ST. |
| 4.2 | **Buck 24V -> 5V (MCU)** | Input 24V, output 5V / 1A, bassa ondulazione | 1 | ~3-6 EUR | AliExpress "LM2596 buck 24V 5V" |
| 4.3 | **Buck 24V -> 6V (servo)** | Input 24V, output 6V / 3A, stall fino a 5A picco | 1 | ~4-8 EUR | AliExpress "buck converter 24V 6V 3A" |
| 4.4 | **Servo metal-gear >= 20 kg*cm** | Digitale, metal gear, torque >= 20 kg*cm a 6V. **OBBLIGATORIA molla di richiamo meccanica** che porta gas a zero senza corrente. Es: JX PDI-6225MG | 1 | ~25-40 EUR | AliExpress "20kg metal gear servo" / Hobbyking |
| 4.5 | **Sensore Hall ACS758 50A** | ACS758LCB-050B, bidirezionale, tra Buck e batteria, ADC STM32 | 1 | ~8-15 EUR | Mouser "ACS758" / AliExpress "ACS758 50A" |
| 4.6 | **Sensore Hall RPM A3144** | Digitale, 1 impulso/giro, robusto all'EMI. Abbinare a magnete sull'albero | 2 | ~2-4 EUR | AliExpress "A3144 hall sensor" |
| 4.7 | **Magnete neodimio N52 diam. 8mm** | Diam. 8mm, spessore 3mm, trigger per RPM Hall | 2 | ~2-3 EUR | AliExpress "N52 neodymium 8mm disc" |
| 4.8 | **Modulo relay 5V kill ignizione** | Relay optoisolato, bobina 5V, contatti 12V / 5A per messa a massa CDI Honda | 1 | ~3-6 EUR | AliExpress "5V relay module optocoupler" |
| 4.9 | **TVS Diode 33V** | Unidirezionale 33V. Es: P6KE33A. Protegge alimentazione MCU da transienti GX50 | 2 | ~1-2 EUR | Mouser / Farnell |
| 4.10 | **Filtro alimentazione MCU** | Elettrolitico 470uF/35V + ceramico 100nF/50V tra buck 5V e MCU | 3+3 | ~2-3 EUR | AliExpress / Mouser |
| 4.11 | **Partitore Vdc (resistori 1%)** | R1=680 kOhm, R2=10 kOhm, tolleranza 1%. Partitore ADC per lettura Vdc fino a 100V | 4 pz | ~1-2 EUR | AliExpress "metal film resistor 1%" |

**Subtotale: ~66-109 EUR**

---

## 5. STRUTTURA MECCANICA

| # | Componente | Specifica Esatta | Qt. | Costo Est. | Note |
|:--|:-----------|:-----------------|:----|:----------:|:-----|
| 5.1 | **Piastra acciaio S235, 5-6mm** | Min. **40x55 cm**, spessore 5 o 6mm, supporto GX50 + BLDC | 1 | ~20-35 EUR | Carpenteria / taglio laser. Richiedere foratura su disegno |
| 5.2 | **Staffa a L alluminio** | Spessore >= 5mm, ~20 cm, supporto frontale flangia BLDC | 1 | ~10-15 EUR | Ferramenta / profili alluminio |
| 5.3 | **Distanziali filettati M6** | Acciaio, altezza 20-30mm, rialzo GX50 dalla piastra per serbatoio inferiore | 4 | ~5-8 EUR | Ferramenta / AliExpress "M6 standoff 25mm" |
| 5.4 | **Silent-block M8, 40-50 Shore A** | Gomma morbida, attacco M8 maschio/femmina, isolamento vibrazioni | 4 | ~10-16 EUR | AliExpress "M8 rubber anti-vibration mount" |
| 5.5 | **Tubolare S235 25x25x2mm** | Per gabbia sotto-telaio, ~2.5 m lineari | 1 barra | ~15-20 EUR | Carpenteria / distributori Marcegaglia |
| 5.6 | **Bulloneria M6/M8 classe 8.8** | Bulloni M6x20, M8x30, dadi Nyloc, rondelle | 1 kit | ~8-12 EUR | Ferramenta |
| 5.7 | **Piastra alluminio 3mm** | ~25x15 cm, supporto/dissipatore SQL100A + Buck + condensatori | 1 | ~5-8 EUR | Ferramenta alluminio |

**Subtotale: ~73-114 EUR**

---

## 6. CABLAGGIO E CONNETTORI

| # | Componente | Specifica Esatta | Qt. | Costo Est. | Note |
|:--|:-----------|:-----------------|:----|:----------:|:-----|
| 6.1 | **Cavo silicone AWG10** (rosso + nero) | 5.26 mm2, ~55A portata, alta flessibilita, 3m/colore | 6 m | ~10-18 EUR | AliExpress "AWG10 silicone wire" |
| 6.2 | **Connettori XT90** | Maschio + femmina XT90, 45A nominale, 90A picco | 2 pairs | ~5-8 EUR | AliExpress / Hobbyking |
| 6.3 | **Connettori Anderson SB50 24V** | Standard industriale, resistente polvere (alternativa XT90) | 1 pair | ~8-12 EUR | RS Components |
| 6.4 | **Cavo silicone AWG22** (segnali) | Sensori, ADC, PWM, relay. ~5 m totali | 5 m | ~3-5 EUR | AliExpress "AWG22 silicone" |
| 6.5 | **Passacavi gomma + fascette 3x200mm** | Passacavi per fori piastra + fascette nylon pack 100 pz | 1 kit | ~3-5 EUR | Ferramenta |
| 6.6 | **Termorestringente 2:1** | Diam. 3-12mm, colori diversi | 1 kit | ~3-5 EUR | AliExpress / Amazon |
| 6.7 | **Capicorda crimpati AWG10** | Forcella + occhio, M4/M6/M8, per sezione AWG10, 50 pz | 1 pack | ~5-8 EUR | Ferramenta elettrica |

**Subtotale: ~37-61 EUR**

---

## 7. SICUREZZA (OBBLIGATORIA — non derogabile)

| # | Componente | Specifica Esatta | Qt. | Costo Est. | Note |
|:--|:-----------|:-----------------|:----|:----------:|:-----|
| 7.1 | **Monitor CO portatile** | Soglia allarme <= 35 ppm, batteria autonoma, display digitale | 1 | ~20-35 EUR | Amazon IT "rilevatore CO portatile" — IL GX50 NON SI ACCENDE SENZA QUESTO |
| 7.2 | **Estintore 1 kg classe ABC** | Polvere ABC (liquidi infiammabili + fuochi elettrici), entro 3 m dal banco | 1 | ~15-25 EUR | Amazon / antincendio — IL GX50 NON SI ACCENDE SENZA QUESTO |
| 7.3 | **Schermo termico inox 304** | Lamierino 0.5mm, ~20x15 cm, separazione tra scarico GX50 e elettronica | 1 | ~8-12 EUR | Ferramenta / carpenteria inox |

**Subtotale: ~43-72 EUR**

---

## 8. SERBATOIO CARBURANTE AGGIUNTIVO

| # | Componente | Specifica | Qt. | Costo Est. | Note |
|:--|:-----------|:----------|:----|:----------:|:-----|
| 8.1 | **Tank HDPE 1L** | Serbatoio benzina HDPE 1L, tappo sigillato, raccordo diam. 8mm | 1 | ~10-15 EUR | AliExpress "gasoline tank HDPE 1L" |
| 8.2 | **Tubo benzina NBR diam. 8mm** | Gomma NBR resistente ai carburanti, 0.5 m + 2 fascette a vite | 1 | ~3-5 EUR | Ferramenta auto / moto |
| 8.3 | **Bacinella raccogligocce PP** | Plastica PP, ~30x20 cm | 1 | ~5-8 EUR | Ferramenta |

**Subtotale: ~18-28 EUR**

---

## 9. CONSUMABILI

| # | Componente | Specifica | Qt. | Costo Est. |
|:--|:-----------|:----------|:----|:----------:|
| 9.1 | **Pasta termica** | MX-4 o equivalente, per SQL100A + Buck | 1 sir. | ~5-8 EUR |
| 9.2 | **Olio motore 4T SAE 10W-30** | Per GX50, ~100 ml carter | 250 ml | ~3-5 EUR |
| 9.3 | **Viti M3/M4 per elettronica** | Assortito 6-20mm per STM32, relay, sensori | 1 kit | ~3-5 EUR |

**Subtotale: ~11-18 EUR**

---

## RIEPILOGO TOTALE

| Categoria | Min | Max |
|:----------|:---:|:---:|
| 1. Gruppo Termico + PTO | 266 EUR | 356 EUR |
| 2. Alternatore BLDC 80100 | 80 EUR | 120 EUR |
| 3. Elettronica di Potenza | 76 EUR | 121 EUR |
| 4. Micro-ECU STM32 + sensori | 66 EUR | 109 EUR |
| 5. Struttura meccanica | 73 EUR | 114 EUR |
| 6. Cablaggio e connettori | 37 EUR | 61 EUR |
| 7. Sicurezza (obbligatoria) | 43 EUR | 72 EUR |
| 8. Serbatoio carburante | 18 EUR | 28 EUR |
| 9. Consumabili | 11 EUR | 18 EUR |
| **TOTALE** | **670 EUR** | **999 EUR** |

**Stima realistica: 750-850 EUR** (spedizioni AliExpress incluse).

---

## CHECKLIST ORDINI

### Ordinare SUBITO — P0 (tempi lunghi o difficile reperimento)
- [ ] Honda GX50 (#1.1) — rivenditore Honda o eBay
- [ ] BLDC 80100 Kv120 (#2.1) — AliExpress: 2-4 settimane spedizione
- [ ] Buck CC/CV 1500W (#3.4)
- [ ] SQL100A + dissipatore (#3.1, #3.2)
- [ ] STM32 Nucleo-F446RE (#4.1) — Mouser/Farnell
- [ ] Servo metal-gear >= 20 kg*cm (#4.4)
- [ ] ACS758 50A (#4.5)

### Ordinare PRIMA DEL MONTAGGIO — P1
- [ ] Frizione 9T + asse millerighe (#1.2, #1.3)
- [ ] Cuscinetto KP08 (#1.4)
- [ ] Pulegge HTD 5M x2 + cinghia x2 (#1.5, #1.6, #1.7)
- [ ] Loctite 638/648 ORIGINALE (#1.9)
- [ ] Piastra acciaio 5mm (#5.1) + staffa L (#5.2)
- [ ] Silent-block M8 x4 (#5.4)
- [ ] Cavo AWG10 + XT90 (#6.1, #6.2)
- [ ] Diodo ideale 50A (#3.5)
- [ ] Condensatori 100V 4700uF x3 marca Nichicon/Rubycon (#3.3)

### Ordinare PRIMA DEL TEST A BANCO — P2 (sicurezza obbligatoria)
- [ ] Monitor CO (#7.1) — senza questo il GX50 non si accende
- [ ] Estintore ABC 1 kg (#7.2) — senza questo il GX50 non si accende
- [ ] Serbatoio HDPE 1L + tubo benzina (#8.1, #8.2)
- [ ] Schermo termico inox (#7.3)

---

## AVVERTENZE CRITICHE

**LOCTITE ORIGINALE OBBLIGATORIA**
Usare solo Loctite 638/648 originale Henkel o Loxeal 83-21. Le colle clone cinesi cedono sotto le vibrazioni del monocilindrico GX50 e causano lo sgranimento del millerighe 9T in poche ore di esercizio.

**CONDENSATORI DI MARCA AFFIDABILE**
I condensatori 100V 4700uF devono essere Nichicon, Rubycon, Panasonic o EPCOS. I generici cinesi non certificati possono esplodere o degradarsi rapidamente alle tensioni operative (50-55V DC con transienti di carico).

**VERIFICARE Kv DEL BLDC PRIMA DEL MONTAGGIO**
Misurare il Kv reale con tachimetro ottico. Formula: V_DC = (RPM / Kv) * 1.414 * 0.95
A 6500 RPM, Kv=130 -> circa 50V DC grezza -> Buck input nel range operativo (15-90V).

**MONOSSIDO DI CARBONIO — PERICOLO MORTALE**
Il GX50 non si accende MAI in ambienti chiusi o senza ventilazione forzata con scarico verso l'esterno. Il CO e' inodore, incolore e letale. Monitor CO (#7.1) obbligatorio ad ogni test.
