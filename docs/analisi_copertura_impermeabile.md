# Analisi: Copertura Impermeabile per Batterie e Componenti Elettronici

**Data:** 2026-06-13  
**Autore:** Analisi tecnica su richiesta  
**Scope:** Valutare la necessità di una copertura impermeabile per le batterie e gli altri componenti sensibili del rover "Mulo" MK0

---

## 1. Stato Attuale della Protezione

### 1.1 Livelli di Protezione Esistenti

| Componente | Livello IP | Materiale | Posizione | Note |
|:---|:---:|:---|:---|:---|
| **Pacco Batteria LiFePO4 24V 100Ah** | **IP67** | Case metallico protettivo + guide antivibranti | Vano batteria (30-55cm altezza) | Case separato con guarnizione stagna; BMS integrato dentro il case |
| **Box Elettronico (Jetson, VESC, CAN, DC-DC)** | **IP68** | Alluminio stagno | Semitelaio posteriore | Tenuta superiore; pad termico dissipativo; silent-block neoprene |
| **Vano Batteria + Elettronica (complessivo)** | **IP54** | Telaio chiuso | Semitelaio posteriore, 30-55cm da terra | Protezione solo anti-splash; NON stagna |
| **Vano Ricambi** | **IP67** | Alluminio 5083-H321 saldato TIG | Sotto-pianale, tra semitelai | Guarnizione silicone fluoroelastomero; fori di drenaggio |
| **Connettori di Potenza** | **IP68/IP69K** | Anderson SB50, Amphenol, Rosenberger, Neutrik | Ovunque | Tutti i connettori sono stagni |
| **Cablaggio** | **IP68** | WIRE-IP68-KIT | Ovunque | Cablaggio potenza/segnale rugged |
| **Gabbia Range Extender** | **Aperta (N/A)** | Acciaio S235 | Sotto-telaio (0-30cm) | Necessariamente aperta per ventilazione motore termico |

### 1.2 Schema dei Livelli di Protezione

```
                   ╔══════════════════════════════════╗
                   ║   GABBIA ZAINI (APERTA)          ║  ← 55-90cm
                   ║   Zaini / Materiale Trekking      ║
                   ╚══════════════════════════════════╝
                   ════════════════════════════════════  ← Pianale S235
                   ╔══════════════════════════════════╗
                   ║  VANO BATTERIA + ELETTRONICA     ║  ← 30-55cm
                   ║  ┌────────────────────────────┐  ║
                   ║  │ IP68 Box (Jetson/VESC)     │  ║
                   ║  │ IP67 Case Batteria         │  ║  ← PROTEZIONE INTERNA
                   ║  │ IP68 Connettori            │  ║
                   ║  └────────────────────────────┘  ║
                   ║  ════════════════════════════     ║
                   ║  Tenuta generale: IP54 ⚠️        ║  ← PROTEZIONE ESTERNA
                   ╚══════════════════════════════════╝
                   ════════════════════════════════════  ← Traversa telaio
                   ╔══════════════════════════════════╗
                   ║  GABBIA RANGE EXTENDER (APERTA)  ║  ← 0-30cm
                   ║  [ GX50 ] ─── [ BLDC ]           ║
                   ╚══════════════════════════════════╝
```

---

## 2. Analisi dei Rischi Ambientali

### 2.1 Ambiente Operativo del Rover

Il rover "Mulo" MK0 è progettato per trekking in ambiente alpino/montano. I rischi ambientali rilevanti sono:

| Rischio Ambientale | Probabilità | Severità | Durata Tipica |
|:---|:---:|:---:|:---|
| **Pioggia leggera/continua** | ALTA | Bassa | Ore (1-6h) |
| **Pioggia battente/tormenta** | MEDIA | Media | Minuti-ore (0.5-2h) |
| **Neve/bagliaccio** | MEDIA | Media-Bassa | Ore (2-8h) |
| **Fango/splash ruote** | ALTA | Bassa-Media | Continuo durante marcia |
| **Guado torrenti poco profondi** | BASSA | ALTA | Minuti (1-5min) |
| **Condensa interna (cicli termici)** | ALTA | Bassa | Continua (notte/giorno) |
| **Polvere/terreno secco** | MEDIA | Bassa | Continuo durante marcia |
| **Pressione lavaggio (manutenzione)** | BASSA | MEDIA | Minuti |

### 2.2 Valutazione della Protezione Attuale per Scenario

| Scenario | Protezione Attuale | Livello Richiesto | Verdetto |
|:---|:---:|:---:|:---:|
| Pioggia leggera (1-2h) | IP54 vano + IP67 batteria | IP54 | ✅ SUFFICIENTE |
| Pioggia battente (>2h) | IP54 vano + IP67 batteria | IP65-IP66 | ⚠️ MARGINALE — acqua può entrare nel vano |
| Neve/bagliaccio | IP54 vano + IP67 batteria | IP54 | ✅ SUFFICIENTE (la neve non penetra facilmente) |
| Fango/splash continuo | IP54 vano + IP67 batteria | IP55-IP66 | ⚠️ MARGINALE — splash ripetuti possono superare IP54 |
| Guado torrente (>20cm) | IP54 vano + IP67 batteria | IP67-IP68 | ❌ INSUFFICIENTE — il vano si allaga; solo la batteria IP67 sopravvive |
| Condensa interna | IP54 vano (no drenaggio) | IP65 + drenaggio | ⚠️ RISCHIOSO — condensa si accumula senza scarico |
| Lavaggio ad alta pressione | IP54 vano | IP69K | ❌ INSUFFICIENTE |

---

## 3. Verdetto: Serve una Copertura Impermeabile?

### 3.1 Il pacco batteria è già protetto (IP67)

Il case metallico del pacco batteria LiFePO4 24V 100Ah è classificato **IP67**, ovvero:
- **6** = Protezione totale contro la polvere (nessun ingresso)
- **7** = Protezione contro l'immersione temporanea in acqua (fino a 1m per 30 minuti)

Questo livello di protezione è **eccellente** per un veicolo off-road. La batteria stessa è al sicuro dalla pioggia, dal fango e perfino da guadi superficiali.

### 3.2 Il Vano è il punto debole (IP54)

Il **vano complessivo** che ospita batteria + elettronica è classificato **IP54**:
- **5** = Protezione polvere limitata (ingresso consentito ma non interferisce col funzionamento)
- **4** = Protezione contro lo splash d'acqua da qualsiasi direzione

IP54 **NON protegge** contro:
- Acqua che entra dall'alto (pioggia battente diretta)
- Acqua che entra dal basso (fango, puddles)
- Jet d'acqua (lavaggio)
- Immersione parziale

### 3.3 Ma la elettronica critica è già al sicuro

L'architettura attuale ha una **protezione a livelli** (defense-in-depth):

1. **Livello 1 — Vano IP54:** Prima barriera. Lenta ma non impermeabile.
2. **Livello 2 — Box Elettronico IP68:** Protegge Jetson, VESC, CAN, DC-DC. **Completamente stagno.**
3. **Livello 3 — Case Batteria IP67:** Protegge celle e BMS. **Praticamente stagno.**
4. **Livello 4 — Connettori IP68/IP69K:** Tutti i collegamenti sono stagni.

Anche se l'acqua entra nel vano IP54, i componenti critici (batteria, elettronica, connettori) sono già protetti da barriere aggiuntive IP67/IP68.

---

## 4. Raccomandazioni

### 4.1 Valutazione Finale: È necessaria una copertura impermeabile aggiuntiva?

**La risposta breve è: NO, per la maggior parte degli scenari.**

Il sistema attuale a livelli multipli di protezione (IP54 vano → IP67 batteria → IP68 elettronica → IP68 connettori) è **sufficiente** per le normali condizioni di trekking in montagna.

Tuttavia, esistono scenari limite dove un miglioramento sarebbe benefico.

### 4.2 Miglioramenti Consigliati (Prioritizzati)

#### PRIORITÀ P0 — Essenziale (da fare subito)

| Intervento | Costo Stimato | Beneficio |
|:---|:---:|:---|
| **Aggiungere guarnizione EPDM/silicone al vano batteria** per portare il vano da IP54 a IP65 | €15-30 | Elimina ingresso pioggia laterale e condensa |
| **Fori di drenaggio con valvola** sul fondo del vano batteria (per evacuare acqua eventualmente entrata) | €5-10 | Previene ristagno d'acqua che potrebbe danneggiare fissaggi e cablaggi |

#### PRIORITÀ P1 — Consigliato (per trekking in condizioni estreme)

| Intervento | Costo Stimato | Beneficio |
|:---|:---:|:---|
| **Tendina/pannello deflettore in TPU** sopra il vano batteria (tipo para-fango superiore) | €20-40 | Blocca pioggia battente diretta e neve che entra dal vano |
| **Tappi in silicone** per i passacavi IP68 quando il rover non è in ricarica | €5-10 | Elimina il punto più debole di ogni sistema stagni: le pene di ingresso cavi |

#### PRIORITÀ P2 — Opzionale (solo per uso estremo)

| Intervento | Costo Stimato | Beneficio |
|:---|:---:|:---|
| **Cover in tessuto laminato impermeabile (TPU)** che copre l'intero semitelaio posteriore | €40-80 | Protezione completa da pioggia, neve, fango per tutti i componenti del vano |
| **Barriera termica aggiuntiva** tra vano batteria e gabbia range extender | €10-20 | Riduce condensa da differenza di temperatura (calore motore termico vs batteria fredda) |

### 4.3 Cosa NON fare

| ❌ Sconsigliato | Motivo |
|:---|:---|
| Aggiungere una scatola chiusa attorno alla batteria con guarnizioni IP68 | La batteria ha già un case IP67; aggiungere un'altra scatola aumenta peso (2-3 kg), riduce accessibilità e può creare problemi di surriscaldamento (la batteria ha bisogno di respirare) |
| Sigillare ermeticamente il vano senza fori di drenaggio | Se l'acqua entra (e prima o poi entra), non avendo vie di uscita rimane intrappolata e causa corrosione |
| Usare silicone strutturale per chiudere i vani | Rende impossibile l'accesso per manutenzione; viola il principio di manutenibilità sul campo (§9 delle specifiche) |

---

## 5. Confronto con Standard Industriali

| Standard | Requisito | Rover Mulo (Attuale) | Verdetto |
|:---|:---|:---:|:---:|
| **IEC 60529** (Classificazione IP) | IP54 = splash + polvere limitata | ✅ Vano | Sufficiente per trekking normale |
| **IEC 60529** | IP67 = immersione 1m/30min | ✅ Batteria case | Eccellente |
| **ISO 20653** (Veicoli stradali) | IP5K4 minimo per componenti sotto-telaio | ✅ | Conforme |
| **SAE J1475** (Veicoli elettrici) | Impermeabilità batteria consigliata IP67+ | ✅ Case batteria IP67 | Conforme |

---

## 6. Conclusione

**Il rover "Mulo" MK0 ha già una protezione adeguata per le batterie e i componenti elettronici critici.** L'architettura a livelli multipli (IP54 vano → IP67 case batteria → IP68 box elettronico → IP68 connettori) offre una difesa sufficiente per le normali condizioni di trekking in montagna.

**Non è necessaria una copertura impermeabile aggiuntiva** come scatola o tenda dedicata. Tuttavia, i seguenti interventi a basso costo migliorano significativamente la robustezza:

1. **Guarnizione EPDM sul vano batteria** (da IP54 a IP65) — €15-30
2. **Fori di drenaggio con valvola** — €5-10
3. **Tappi silicone per passacavi** — €5-10

**Costo totale consigliato: ~€25-50** per un miglioramento sostanziale della protezione.

Il design attuale è **consapevole e corretto**: la batteria è protetta dal suo case IP67, l'elettronica dal box IP68, e i connettori sono tutti IP68/IP69K. Il vano IP54 è la "prima linea di difesa" imperfetta ma compensata dalle protezioni interne.

---

*Riferimenti: hardware/bom.md, docs/mulo_mk0_hardware_specs.md §10, docs/mulo_mk0_range_extender_diy.md §6, engineering_recommendations.md §7*