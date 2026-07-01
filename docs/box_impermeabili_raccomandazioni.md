# Raccomandazioni Box Impermeabili per Rover Mulo MK0

**Data:** 2026-06-13  
**Scopo:** Fornire raccomandazioni concrete per box impermeabili (IP67/IP68) per batterie, elettronica e componenti sensibili del rover.

---

## 1. Riassunto dei Requisiti

| Componente | Dimensioni interne necessarie | Peso | IP minimo | Note |
|:---|:---|:---:|:---:|:---|
| **Vano batteria + elettronica** | ~600 × 300 × 280 mm | - | IP65+ | Il vano attuale è IP54 |
| **Batteria LiFePO4 24V 100Ah** | 520 × 240 × 220 mm | 23 kg | IP67 | Case già IP67; il box è il contenitore esterno |
| **Jetson + VESC + CAN + DC-DC** | ~400 × 250 × 200 mm | ~6 kg | IP68 | Box dedicato |

---

## 2. Consigli per il Vano Batteria (da IP54 a IP67)

### 2.1 — Soluzione 1: Box Alluminio Zarges (Consigliata)

- **Modello:** Zarges K470 470×300×220 mm (oppure K480 per 600×400×200)
- **Materiale:** Alluminio 5052-H32, anti-corrosione
- **IP:** IP67 con guarnizione EPDM
- **Peso:** ~2.5-3.0 kg
- **Prezzo:** €120-180 (Amazon/RS Components)
- **Link:** [zarges.com](https://www.zarges.com) / RS Components / Amazon
- **Perché è ideale:**
  - Guarnizione EPDM resistente a temperature estreme (-40°C a +120°C)
  - Coperchio con bulloneria classica (non ad apertura rapida, ma con 4 bulloni M8)
  - Resiste a urti e vibrazioni tipiche dei veicoli
  - Disponibile in varianti con fori di drenaggio già integrati
  - Usato industrialmente per radar militari e sistemi elettronici marine

### 2.2 — Soluzione 2: Pelican 1650 Case (Militare/Marine)

- **Modello:** Pelican 1650 Protector Case
- **Dimensioni interne:** 606 × 406 × 229 mm
- **Materiale:** Polietilene ad alta densità (HDPE)
- **IP:** IP67 (testato per immersione 1m/30min)
- **Peso:** ~4.5 kg (più pesante, ma molto resistente)
- **Prezzo:** €100-150 (Amazon/eBay)
- **Perché è ideale:**
  - Testato secondo standard militari (MIL-STD-810G)
  - Resistente a corrosione, urti, polvere, pioggia battente
  - Coperchio a scatto rapido con 2 chiusure
  - Guarnizione in EPDM perfettamente stagna
  - Usato da forze speciali e riprese subacquee

### 2.3 — Soluzione 3: Box custom in alluminio (su misura)

Se avete accesso a un laboratorio CNC:

```yaml
spec:
  material: "Alluminio 6061-T6"
  thickness: "2 mm"
  dimensions:
    internal: "600 × 300 × 280 mm"
    external: "610 × 310 × 290 mm (con guarnizione)"
  seal: "Guarnizione EPDM 5 mm"
  drainage: "2 fori 8mm con valvola a sfera"
  mounting: "4x bulloni M8 a sgancio rapido (Dzus)"
  finish: "Anodizzazione defelettiva"
  weight: "~3.0 kg"
  cost: "€150-250 (officina locale)"
```

---

## 3. Consigli per Box Elettronico (Jetson, VESC, DC-DC)

### 3.1 — Soluzione 1: Eaton Boxtop IP68 (Industriale)

- **Modello:** Eaton Boxtop IP68 Series
- **Materiale:** Alluminio pressofuso con finitura epoxi
- **IP:** IP68 (prova di immersione 1m/24h)
- **Peso:** ~2.0 kg
- **Prezzo:** €120-180 (RS Components/Mouser)
- **Perché è ideale:**
  - Resistenza a pressione e immersione prolungata
  - Dissipazione termica integrata (pareti in alluminio)
  - Finitura anti-corrosione per uso marino
  - Dimensioni flessibili (da 200×150×100mm a 500×400×200mm)

### 3.2 — Soluzione 2: Hammond 1550 IP68 (Economico)

- **Modello:** Hammond 1550 Series IP68
- **Materiale:** Alluminio con guarnizione silicone
- **IP:** IP68 (prova di immersione 1m/30min)
- **Peso:** ~1.5 kg
- **Prezzo:** €60-100 (Amazon/DigiKey)
- **Perché è ideale:**
  - Economico ma affidabile
  - Guarnizione in silicone resistente a temperature
  - Disponibile in molte dimensioni (ideale per 400×250×200mm)
  - Montaggio a parete o su staffa

### 3.3 — Soluzione 3: Box custom con dissipatore (ottimale per VESC)

```yaml
spec:
  material: "Alluminio 6061-T6"
  thickness: "3 mm (pareti dissipanti)"
  dimensions:
    internal: "400 × 250 × 200 mm"
  seal: "Guarnizione fluoroelastomero FKM 5mm"
  thermal: "Pareti interne come dissipatore (finitura nera anodizzata)"
  mounting: "Staffe a Vibrazioni con silent-block neoprene 40 Shore"
  cost: "€100-180 (officina CNC)"
```

---

## 4. Consigli per Box Vano Ricambi (già IP67)

Il vano ricambi è già IP67 (alluminio 5083-H321). Non serve sostituirlo. Tuttavia, se volete aggiungere una **seconda barriera** interna per proteggere i ricambi da condensa:

- **Opzione:** Pelican 1200 Case (dimensioni: 240×170×100mm, IP67, €30-40)
- **Opzione:** Sacchetto stagno in politene con chiusura a cerniera (€5-10 per 10 pezzi)

---

## 5. Tabella Riassuntiva: Consigli per Componente

| Componente | Box Consigliato | IP | Prezzo | Reperibilità |
|:---|:---|:---:|:---:|:---|
| **Vano batteria + elettronica** | Zarges K480 600×400×200 | IP67 | €120-180 | Amazon / RS Components |
| **Alternativa economica vano** | Pelican 1650 | IP67 | €100-150 | Amazon / eBay |
| **Jetson + VESC** | Hammond 1550 (400×250×200) | IP68 | €60-100 | Amazon / DigiKey |
| **Alternativa industriale** | Eaton Boxtop IP68 | IP68 | €120-180 | RS Components |
| **Vano ricambi** | Già IP67 (non cambiare) | IP67 | €0 | - |
| **Range Extender elettronica** | Hammond 1550 (200×150×100) | IP68 | €40-60 | Amazon |
| **Accessori** | Tappi silicone per passacavi | IP68 | €5-10 | Amazon |

---

## 6. Accessori Essenziali

| Accessorio | Scopo | Prezzo |
|:---|:---|:---|
| **Tappi silicone per passacavi IP68** | Sigillare ingresso cavi quando non in ricarica | €5-10 (kit 10 pezzi) |
| **Guarnizione EPDM 5mm (rotolo)** | Sigillare coperchio vano batteria | €8-15 |
| **Valvole di drenaggio IP67** | Evacuare acqua eventualmente entrata nel vano | €3-5 cad. |
| **Silent-block neoprene 40 Shore** | Isolamento vibrazioni tra box e telaio | €2-4 cad. |
| **Bulloni M8 a sgancio rapido (Dzus)** | Accesso rapido al vano senza attrezzi | €3-5 cad. |

---

## 7. Schema di Montaggio Consigliato

```
╔════════════════════════════════════════════════════════╗
║               TELAIO S235 (Traversa posteriore)        ║
╠════════════════════════════════════════════════════════╣
║  ┌──────────────────────────────────────────────────┐  ║
║  │  SILENT-BLOCK NEOPRENE 40 Shore (4x)             │  ║
║  └──────────────────────────────────────────────────┘  ║
║  ┌──────────────────────────────────────────────────┐  ║
║  │  ZARGES K480 — VANO BATTERIA + ELETTRONICA      │  ║
║  │  IP67 con guarnizione EPDM                       │  ║
║  │                                                  │  ║
║  │  ┌────────────────────────────────────────────┐  │  ║
║  │  │  BATTERIA LiFePO4 24V 100Ah                │  │  ║
║  │  │  (Case IP67 incluso)                        │  │  ║
║  │  └────────────────────────────────────────────┘  │  ║
║  │                                                  │  ║
║  │  ┌────────────────────────────────────────────┐  │  ║
║  │  │  HAMMOND 1550 — BOX ELETTRONICO IP68       │  │  ║
║  │  │  Jetson / VESC / CAN / DC-DC               │  │  ║
║  │  └────────────────────────────────────────────┘  │  ║
║  │                                                  │  ║
║  │  FORI DI DRENNAGGIO IP67 (x2) + VALVOLA         │  ║
║  └──────────────────────────────────────────────────┘  ║
║  4x BULLONI M8 A SGANCIO RAPIDO (Dzus)                ║
╚════════════════════════════════════════════════════════╝
```

---

## 8. Confronto Costi Totali

| Scenario | Componenti | Costo Stimato |
|:---|:---|:---:|
| **Minimalista (tutto il necessario)** | Zarges K480 + Hammond 1550 + accessori | €200-300 |
| **Robusto (militare/marine)** | Pelican 1650 + Eaton Boxtop + accessori | €280-400 |
| **Custom (tutto su misura)** | Box custom CNC + accessori | €300-500 |

**Raccomandazione finale:** Lo scenario **minimalista** (Zarges + Hammond + accessori) è il più equilibrato tra costo, protezione e reperibilità in Italia.

---

*Riferimenti: docs/analisi_copertura_impermeabile.md, hardware/bom.md, docs/mulo_mk0_hardware_specs.md*