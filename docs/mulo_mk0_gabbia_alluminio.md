# Gabbia Porta-Zaini in Alluminio per Mulo MK0

## 1. Concept

Una gabbia leggera in profilato d'alluminio che si innesta sopra il pianale del telaio tubolare S235, progettata per ospitare il carico leggero (zaini, tenda, sacco a pelo, abbigliamento, viveri) fino a ~30 kg, mantenendo il baricentro entro limiti di sicurezza.

La gabbia **non** sostituisce il pianale a 55 cm — lo completa, offrendo un volume superiore per lo stivaggio senza compromettere la stabilità.

---

## 2. Materiali

### Profilato Consigliato: Alluminio 6061-T6

| Grandezza | Profilo | Note |
|---|---|---|
| **Montanti verticali** | Tubolare 20×20×1.5 mm | Leggero, rigido a flessione |
| **Traverse orizzontali** | Tubolare 20×20×1.5 mm | Stessa sezione, semplifica il taglio |
| **Angolari di rinforzo** | Squadretta in alluminio 25×25×2 mm | Da imbullonare agli angoli |
| **Piano di base** | Reticolo di alluminio 10×10×1 mm (espanso) | Opzionale: per appoggiare gli zaini |

**Perché 6061-T6:** resistenza meccanica buona (~310 MPa a trazione), saldabile TIG, facilmente lavorabile con attrezzi manuali. Peso specifico 2.7 g/cm³ — un terzo dell'acciaio.

### Alternative al 6061-T6 (se trovi meglio in commercio):
- **Alluminio 6082-T6:** simile, più comune in Europa, leggermente più resistente
- **Alluminio 6005A-T6:** usato nei telai per roulotte, ben bilanciato

### Sconsigliato:
- Alluminio 1050 o 1070 (puro): troppo tenero, non tiene carichi strutturali
- Alluminio 2024-T3: ottimo meccanicamente ma non saldabile in officina

---

## 3. Geometria della Gabbia

```
            Vista Frontale
    ┌──────────────────────────────┐
    │  ┌──┬──┬──┬──┬──┬──┬──┬──┐  │  ← Traversa superiore (larghezza 60cm)
    │  │  │  │  │  │  │  │  │  │  │
    │  │  │  │  │  │  │  │  │  │  │  ← Montanti verticali ogni ~8 cm
    │  │  │  │  │  │  │  │  │  │  │
    │  │  │  │  │  │  │  │  │  │  │
    │  └──┴──┴──┴──┴──┴──┴──┴──┘  │  ← Piano di base (aggancio al telaio)
    └──────────────────────────────┘
         ←──── 60 cm ────→

           Vista Laterale
        ┌────────────────────────┐ 
        │▌  ╔════════════╗      ▌│  ← Zaini (max 100cm)
        │▌  ║  ZAINO     ║      ▌│
        │▌  ║            ║      ▌│
        │▌  ╚════════════╝      ▌│
        │▌  ┌────────────┐      ▌│  ← Piano di base gabbia (55cm dal suolo)
        │▌  │            │      ▌│  = stesso piano del pianale MK0
        │▌  └────────────┘      ▌│
        │▌  ════════════════    ▌│  ← Telaio tubolare S235 (30x30x2mm)
        └────────────────────────┘
    ← 30cm →          ← 30cm →
```

### Dimensioni Consigliate

| Parametro | Valore | Note |
|---|---|---|
| **Larghezza** | 60 cm | Uguale alla carreggiata, filo esterno telaio |
| **Profondità** | 50 cm | Dal bordo anteriore al posteriore del pianale |
| **Altezza gabbia** | 35-45 cm | Dal pianale (55cm) alla sommità: totale 90-100cm da terra |
| **Altezza totale da terra** | 90-100 cm | Dipende da quanti zaini vuoi impilare |

### Altezza consigliata: 35 cm (totale 90 cm da terra)
Con un carico di 30 kg distribuito, il CoG si attesta a ~40 cm → **angolo limite 37°** — eccellente per sentiero.

---

## 4. Struttura Dettagliata

### 4.1 Telaio di Base
Un rettangolo di profilato 20×20×1.5 mm delle stesse dimensioni del pianale MK0 (60×50 cm). Questo rettangolo si fissa direttamente sopra il pianale in acciaio S235 con **bulloneria passante M6**.

### 4.2 Montanti Verticali
- **8 montanti**: 4 agli angoli + 4 intermedi (2 per lato lungo)
- Altezza: 35 cm dal piano di base
- I montanti si imbullonano o si saldano TIG alla base

### 4.3 Traverse Superiori (Cintura Superiore)
- Un secondo rettangolo 60×50 cm in cima ai montanti
- Chiude la struttura e impedisce l'apertura laterale

### 4.4 Rinforzi Diagonali (Opzionali ma Consigliati)
- Per evitare che la gabbia "romboide" sotto sforzo laterale (scenario: rover inclinato su traversa), aggiungi **4 diagonali** in profilato 15×15×1.5 mm:
  - 2 diagonali sulla faccia anteriore (dall'angolo basso a quello alto opposto)
  - 2 diagonali sulla faccia posteriore

### 4.5 Reticolo di Fondo (Opzionale)
Un foglio di reticolato in alluminio espanso (spessore 1-2 mm) saldato o rivettato al telaio di base crea un piano d'appoggio continuo per gli zaini, impedendo che cadano attraverso la struttura. In alternativa: una lastra di compensato marino da 6 mm trattato con impregnante (pesa solo ~3 kg ed evita l'usura dello zaino sulla struttura metallica).

---

## 5. Sistema di Fissaggio al Telaio MK0

> **Regola d'oro:** la gabbia deve essere **smontabile** (Quick-Split compatibile) e **non deve indebolire il telaio principale.**

### Opzione A: Bullonatura Passante (Consigliata)
```
                             ┌──────────────────────────────┐
                             │   Gabbia alluminio 20×20      │
                             │   ┌───┐                       │
               ┌───┐         │   │M6│                       │
               │ M6│         │   └───┘                       │
               └───┘         └──────────────────┬───────────┘
                    │                            │ 
                    │  ──────────────────────────┤  Piastra d'acciaio da 3mm
                    │         ┌──────────────────┤  (adattatore acciaio→alluminio)
                    ├─────────┤                  │
                    │         └──────────────────┤
                    │                            │ 
               ┌──────────────────────────────┐  │
               │   Telaio S235 30×30×2 mm     │──┘
               └──────────────────────────────┘
```

**Procedura:**
1. **Piastre adattatrici in acciaio da 3 mm** (tagliate 40×60 mm) vengono **svasate nel tubolare S235** — 4 piastre per il telaio anteriore, 4 per il posteriore, totale 8 piastre.
2. Su ogni piastra adattatrice si salda un **dado M6** o in alternativa si usa un dado autobloccante.
3. La gabbia in alluminio si appoggia sopra le piastre e si fissa con **viti M6×25 mm a testa cilindrica con rondella Grower** (impedisce lo svitamento per vibrazione).
4. **Interponi un foglio di gomma da 1-2 mm** tra alluminio e acciaio per evitare corrosione galvanica (alluminio + acciaio in ambiente umido = pila galvanica).

### Opzione B: Fissaggio a "Baionetta" (Per smontaggio ultra-rapido)
Adatto se la gabbia deve essere rimossa frequentemente (es. trasporto auto in configurazione Quick-Split):
1. Salda **4 perni da 8 mm** sul telaio S235
2. I montanti della gabbia hanno **boccole forate** corrispondenti
3. Blocca con **coppiglie a sgancio rapido (R-clip o hairpin cotter)**

### Opzione C (SCONSIGLIATA): Saldatura diretta alluminio-acciaio
La saldatura diretta tra alluminio e acciaio è impossibile con metodi convenzionali (i due metalli non si legano). Richiederebbe saldabrazatura con apporto speciale (es. Alloy 4043 su acciaio zincato) — molto fragile e non affidabile sotto vibrazione.

---

## 6. Peso Stimato della Gabbia

| Componente | Materiale | Peso |
|---|---|---|
| Telaio base (60×50cm, perimetro 220cm di profilo 20×20×1.5) | Alluminio 6061-T6 | ~0.60 kg |
| Montanti (8×35cm = 280cm) | Alluminio 6061-T6 | ~0.76 kg |
| Cintura superiore (220cm) | Alluminio 6061-T6 | ~0.60 kg |
| Diagonali (4×70cm = 280cm di profilo 15×15×1.5) | Alluminio 6061-T6 | ~0.41 kg |
| Reticolo fondo (0.6×0.5m di rete 10×10×1mm espanso) | Alluminio | ~0.35 kg |
| **Piastre adattatrici** (8 pezzi 40×60×3mm) | Acciaio S235 | ~0.45 kg |
| **Bulloneria M6** (16 viti + dadi autobloccanti + rondelle) | Acciaio inox A2-70 | ~0.08 kg |
| Guarnizione antigalvanica (foglio gomma 1mm) | Gomma neoprene | ~0.03 kg |
| **TOTALE GABBIA** | | **~3.3 kg** |

Incremento al CoG dovuto alla gabbia stessa: trascurabile (3.3 kg distribuiti sulla struttura).

---

## 7. Accessori Aggiuntivi Consigliati

### 7.1 Punti di Aggancio per Cinghie (Tie-Down)
Aggiungi **4 anelli saldati** (o golfari M6) ai 4 angoli del perimetro superiore della gabbia. Servono per fissare gli zaini con cinghie elastiche o corde elastiche (bungee cords) ed evitare che il carico balli durante il movimento su sentiero sconnesso.

### 7.2 Protezione Antipioggia (Opzionale)
Una **telo copri-carico** in tessuto PVC (peso ~0.5 kg) con coulisse, che si infila sopra la gabbia e protegge zaini e attrezzatura da pioggia e fango durante il trekking. Si ripiega nel bagagliaio quando non serve.

### 7.3 Rete Elastica di Contenimento Superiore
Un **elastic cargo net** (rete elastica da 60×50cm) tesa sulla cintura superiore della gabbia impedisce la fuoriuscita di oggetti piccoli (borraccia, giacca a vento) durante i movimenti bruschi.

---

## 8. Considerazioni Dinamiche

### Vibrazioni e Fatica
L'alluminio 6061-T6 ha un limite di fatica definito (~97 MPa a 5×10⁸ cicli). A 4 km/h, le vibrazioni del terreno sono a bassa frequenza e bassa ampiezza (smorzate dai silent-block e dagli pneumatici a 1.2 bar). Non c'è rischio di rottura per fatica in condizioni normali d'uso.

### Effetto Pendolo (Carico Oscillante)
Gli zaini hanno un comportamento diverso da un carico rigido: oscillano come pendoli. Per ridurre l'effetto pendolo:
1. Fissa gli zaini con cinghie **in diagonale** (dall'anello superiore di un lato a quello inferiore del lato opposto)
2. Non impilare piú di **2 zaini** in altezza
3. Metti lo zaino più pesante in basso, quello più leggero sopra

### Compatibilità con Quick-Split
La gabbia si monta sul pianale superiore del telaio. Quando separi i due semitelai (Quick-Split), devi:
- Opzione facile: togliere la gabbia (8 viti M6)
- Opzione permanente: costruire la gabbia in **due metà** (anteriore e posteriore) che si separano insieme ai semitelai

Se prevedi di usare spesso il Quick-Split, l'Opzione permanente è più comoda: basta realizzare la gabbia divisa con un piccolo giunto di separazione al centro (due viti M6 di collegamento tra le metà anteriore e posteriore).

---

## 9. Riassunto Materiali per l'Acquisto

| Oggetto | Quantità | Costo indicativo |
|---|---|---|
| Profilato alluminio 6061-T6 20×20×1.5 mm (barre da 3m) | 3 barre | ~18-25 € cad. |
| Profilato alluminio 6061-T6 15×15×1.5 mm (barra da 3m) | 1 barra | ~12-15 € |
| Reticolo alluminio espanso 10×10×1 mm (foglio 60×50cm) | 1 foglio | ~10-15 € |
| Piastra acciaio S235 3mm (40×60mm) | 8 pezzi | ~5 € (taglio laser) |
| Viti M6×25 mm testa cilindrica inox A2-70 | 16 pezzi | ~3 € |
| Dadi autobloccanti M6 inox A2 | 16 pezzi | ~2 € |
| Rondelle Grower M6 inox | 16 pezzi | ~1 € |
| Guarnizione gomma neoprene 1mm (foglio) | 1 foglio | ~3 € |
| Anelli di aggancio M6 (golfari) | 4 pezzi | ~4 € |
| **TOTALE MATERIALE** | | **~100-140 €** |

### Tempo di costruzione stimato:
- Taglio profilati: 1 ora (con seghetto per metalli o troncatrice)
- Foratura: 30 minuti (trapano a colonna o trapano avvitatore)
- Bullonatura e montaggio: 1 ora
- **Totale: circa 2.5 ore** (nessuna saldatura richiesta se usi bullonatura + squadrette)

---

## 10. Conclusione

La gabbia in alluminio è:
- **Peso**: ~3.3 kg (leggerissima)
- **Costo**: ~100-140 € di materiale
- **Stabilità**: compatibile con angolo limite di 37° con carico di 30 kg
- **Costruzione**: semplice, attrezzi manuali, niente saldatura
- **Smontabile**: in 5 minuti (8 viti M6)

Costruiscila con giunzioni bullonate + squadrette angolari, oppure se hai accesso a una TIG, salda i giunti in alluminio 6061-T6 con bacchetta ER4043 (le giunzioni bullonate sono più semplici e altrettanto robuste per un carico di 30 kg a 4 km/h).