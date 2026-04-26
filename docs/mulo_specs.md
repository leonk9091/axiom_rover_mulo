# Progetto Rover "Mulo" - Specifiche Tecniche Finali

## 1. Architettura Strutturale: "Reinforced Direct Drive"
Il design è concepito per proteggere i motori da carichi radiali distruttivi utilizzando un sistema a cuscinetti esterni flangiati.

- **Telaio:** Moduli in acciaio 30x30x2mm con **controventature diagonali** anti-deformazione.
- **Snodo di Torsione:** Albero 20mm su cuscinetti **UCP204** con piastra di rinforzo in acciaio da 6mm.
- **Supporto Ruota (Ponte Corazzato):** 
  - Piastra d'acciaio da 6mm interposta.
  - Cuscinetto flangiato **UCF204** (esterno) per scaricare le forze di taglio sul telaio.
  - Motore (interno) protetto dal momento flettente.

## 2. Drivetrain e Alberi Custom
- **Motori:** 4x Stepperonline 24V 200W (71.5:1).
- **Ruote:** 4x Cargo E-bike 20" (Anteriori, mozzo 33-36mm, 6 fori IS).
- **Alberi di Prolunga (42CrMo4):**
  - Lato Motore: Foro 14mm + Cava chiavetta (DIN 6885A).
  - Sezione Centrale: 20mm h6 (accoppiamento perfetto UCF204).
  - Lato Ruota: Flangia per mozzo 6 fori.

## 3. Frenata e Sicurezza Meccanica
- **Elettronica:** Rigenerativa via **Dual FSESC** con Dump Load.
- **Stazionamento:** 4x Pinze meccaniche **Avid BB7** + Dischi 203mm.
- **Controllo:** Leve con cricchetto di blocco (Sistema Bowden).

## 4. Sequenza di Montaggio
1.  **Fase 1 (Carpenteria):** Costruzione moduli e controventature.
2.  **Fase 2 (Snodo):** Installazione UCP204 su piastra da 6mm.
3.  **Fase 3 (Power Assembly):** Montaggio "Sandwich" Staffa/Motore/UCF204 e calettamento alberi 42CrMo4.
4.  **Fase 4 (Integrazione):** Ruote, freni a disco e cablaggio CAN-bus.
