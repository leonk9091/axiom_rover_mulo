"""Generate FreeCAD FCStd/STEP/STL for the MULO-REX controller carrier plate."""

from __future__ import annotations

import pathlib

import FreeCAD as App
import Mesh
import Part

ROOT = pathlib.Path(__file__).resolve().parent
OUT = ROOT / "generated"
OUT.mkdir(exist_ok=True)

LENGTH_MM = 190.0
WIDTH_MM = 120.0
THICKNESS_MM = 4.0
BOX_X_MM = 170.0
BOX_Y_MM = 100.0
NUCLEO_X_MM = 70.0
NUCLEO_Y_MM = 55.0


def cut_hole(shape: Part.Shape, x_mm: float, y_mm: float, diameter_mm: float) -> Part.Shape:
    cutter = Part.makeCylinder(
        diameter_mm / 2.0,
        THICKNESS_MM + 2.0,
        App.Vector(x_mm, y_mm, -1.0),
        App.Vector(0, 0, 1),
    )
    return shape.cut(cutter)


def main() -> None:
    doc = App.newDocument("MULO_REX_Controller_Carrier")
    plate = Part.makeBox(LENGTH_MM, WIDTH_MM, THICKNESS_MM)

    for x in ((LENGTH_MM - BOX_X_MM) / 2.0, (LENGTH_MM + BOX_X_MM) / 2.0):
        for y in ((WIDTH_MM - BOX_Y_MM) / 2.0, (WIDTH_MM + BOX_Y_MM) / 2.0):
            plate = cut_hole(plate, x, y, 4.5)

    for x in ((LENGTH_MM - NUCLEO_X_MM) / 2.0, (LENGTH_MM + NUCLEO_X_MM) / 2.0):
        for y in ((WIDTH_MM - NUCLEO_Y_MM) / 2.0, (WIDTH_MM + NUCLEO_Y_MM) / 2.0):
            plate = cut_hole(plate, x, y, 3.2)

    obj = doc.addObject("Part::Feature", "rex_controller_carrier_plate")
    obj.Shape = plate
    doc.recompute()

    doc.saveAs(str(OUT / "rex_controller_carrier_plate.FCStd"))
    Part.export([obj], str(OUT / "rex_controller_carrier_plate.step"))
    Mesh.export([obj], str(OUT / "rex_controller_carrier_plate_freecad.stl"))


main()
