# Walkthrough: Assemblaggio Meccanico Axiom Rover "Mulo"

Questo documento guida l'assemblaggio basandosi sui disegni tecnici CAD 2D generati.

## 1. Schema Telaio (Layout Generale)
Il telaio è composto da due moduli indipendenti collegati da uno snodo centrale.

![Chassis Layout](file:///A:/progetto%20rover/axiom_rover_ws/hardware/cad/chassis_layout.png)

- **Lunghezza Totale:** ~800mm
- **Larghezza:** ~600mm
- **Materiale:** Tubolare 30x30x2mm Acciaio S235.
- **Snodo:** UCP204 posizionato sulla mezzeria.

## 2. Dettaglio Gruppo Ruota (Sezione)
Il "Ponte Corazzato" utilizza un sistema a sandwich per scaricare il peso.

![Wheel Assembly](file:///A:/progetto%20rover/axiom_rover_ws/hardware/cad/wheel_assembly.png)

### Ordine di Montaggio (dall'interno verso l'esterno):
1.  **Motore Stepperonline**: Avvitato alla piastra da 6mm.
2.  **Piastra Rinforzo (6mm)**: Fissata al tubolare 30x30 del telaio.
3.  **Cuscinetto UCF204**: Imbullonato al lato esterno della piastra da 6mm.
4.  **Albero Custom (42CrMo4)**: Si infila sul motore, attraversa la piastra e il cuscinetto.
5.  **Ruota Cargo 20"**: Imbullonata alla flangia dell'albero.

## 3. Controventature Diagonali (Rinforzo)
Per evitare che il telaio si deformi a "parallelogramma" sotto i 130kg di carico, è fondamentale installare i rinforzi diagonali.

![Chassis Bracing](file:///A:/progetto%20rover/axiom_rover_ws/hardware/cad/chassis_bracing.png)

- **Materiale:** Piatto d'acciaio 20x3mm.
- **Posizionamento:** Incrociare i rettangoli principali dei moduli.
- **Fissaggio:** Bulloni M8 passanti.

## 4. Quote Critiche per la Foratura
- **Distanza Motore-Cuscinetto:** Definita dallo spessore della piastra (6mm).
- **Fori UCF204:** PCD standard per flangia da 20mm.
- **Centratura:** L'asse del motore deve essere perfettamente allineato con il centro del cuscinetto UCF204 per evitare vibrazioni.
