# REX Controller Carrier Mechanical Package

Questa cartella contiene una piastra parametrica iniziale per fissare il
controller STM32 REX dentro un box tecnico. Non e' la piastra del GX50 o della
trasmissione: serve per elettronica, strain relief e review layout.

## File

| File | Uso |
| :--- | :--- |
| `rex_controller_carrier_plate.scad` | Geometria OpenSCAD parametrica. |
| `freecad_rex_controller_carrier.py` | Generatore FreeCAD per FCStd/STEP/STL. |
| `generated/` | Output STL/DXF/STEP/PNG creati dallo script assembly. |

## Quote Baseline

- Piastra: 190 mm x 120 mm x 4 mm.
- Fori box: M4 su rettangolo 170 mm x 100 mm.
- Fori Nucleo/carrier: M3 su pattern 70 mm x 55 mm.
- Asole strain relief: 4 asole 14 mm x 5 mm.

Le quote sono placeholder industrializzabili: prima dell'ordine vanno sostituite
con misure reali di box, Nucleo, morsetti, pressacavi e connettori.
