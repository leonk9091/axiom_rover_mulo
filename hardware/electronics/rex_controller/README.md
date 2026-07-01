# MULO-REX Controller Electronics Package

Data baseline: 2026-06-14

Questo pacchetto raccoglie lo schema elettrico di riferimento per il controller
STM32 separato del range extender Honda GX50.

## Stato Tool

KiCad CLI 10.0.3, WireViz 0.4.1, Graphviz, OpenSCAD 2021.01 e FreeCAD 1.1.1
sono disponibili per generare gli artefatti di assemblaggio. Questo pacchetto
fornisce sia sorgenti rigenerabili sia file importabili/trascrivibili in KiCad:

- netlist logica CSV;
- harness/pinout CSV;
- BOM candidato;
- schema a blocchi Mermaid;
- architettura DOT;
- progetto KiCad funzionale;
- harness WireViz;
- checklist KiCad ERC/DRC per passaggio a PCB finale.

## File

| File | Uso |
| :--- | :--- |
| `rex_controller_harness.csv` | Connettori, pin, segnali e validazioni banco. |
| `rex_controller_netlist.csv` | Nodi elettrici e collegamenti logici. |
| `rex_controller_bom.csv` | Componenti principali e rating minimi. |
| `rex_controller_schematic.mmd` | Schema funzionale in Mermaid. |
| `rex_power_architecture.dot` | Grafo potenza/segnali per review. |
| `kicad_implementation_notes.md` | Passi per creare lo schema KiCad reale. |
| `kicad/mulo_rex_controller` | Baseline KiCad funzionale esportabile in PDF/SVG. |
| `wireviz/rex_controller_harness.yml` | Harness rigenerabile WireViz. |
| `generated/` | Output generati da `scripts/generate_assembly_artifacts.ps1`. |

## Regole

- La safety MCU resta superiore al REX controller.
- `SAFETY_KILL_N` deve spegnere il GX50 anche senza ROS.
- `KILL_IGNITION` deve essere testato con motore spento prima della prima accensione.
- I segnali analogici sono di misura, non di protezione unica: Vdc e corrente richiedono anche protezioni hardware.
- Tutti i rating `TBD` bloccano acquisti o test ad alta energia.
