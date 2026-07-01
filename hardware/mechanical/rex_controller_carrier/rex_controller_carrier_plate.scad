// MULO-REX STM32 controller carrier plate
// Baseline: electronics carrier only, not GX50 engine mount.

plate_length = 190;
plate_width = 120;
plate_thickness = 4;
corner_radius = 6;

box_hole_x = 170;
box_hole_y = 100;
box_hole_d = 4.5;

nucleo_hole_x = 70;
nucleo_hole_y = 55;
nucleo_hole_d = 3.2;

strain_slot_w = 14;
strain_slot_h = 5;

export_2d = false;

module rounded_plate_2d(length, width, radius) {
    hull() {
        translate([radius, radius]) circle(r = radius, $fn = 32);
        translate([length - radius, radius]) circle(r = radius, $fn = 32);
        translate([radius, width - radius]) circle(r = radius, $fn = 32);
        translate([length - radius, width - radius]) circle(r = radius, $fn = 32);
    }
}

module slot_2d(w, h) {
    hull() {
        translate([-w / 2 + h / 2, 0]) circle(d = h, $fn = 24);
        translate([w / 2 - h / 2, 0]) circle(d = h, $fn = 24);
    }
}

module carrier_plate_3d() {
    difference() {
        linear_extrude(height = plate_thickness)
            rounded_plate_2d(plate_length, plate_width, corner_radius);

        // Box mounting holes, M4 clearance.
        for (x = [(plate_length - box_hole_x) / 2, (plate_length + box_hole_x) / 2])
            for (y = [(plate_width - box_hole_y) / 2, (plate_width + box_hole_y) / 2])
                translate([x, y, -1]) cylinder(d = box_hole_d, h = plate_thickness + 2, $fn = 32);

        // STM32/Nucleo carrier standoffs, M3 clearance.
        for (x = [(plate_length - nucleo_hole_x) / 2, (plate_length + nucleo_hole_x) / 2])
            for (y = [(plate_width - nucleo_hole_y) / 2, (plate_width + nucleo_hole_y) / 2])
                translate([x, y, -1]) cylinder(d = nucleo_hole_d, h = plate_thickness + 2, $fn = 32);

        // Cable tie/strain relief slots near connector edge.
        for (y = [30, 50, 70, 90])
            translate([plate_length - 28, y, -1])
                linear_extrude(height = plate_thickness + 2)
                    slot_2d(strain_slot_w, strain_slot_h);

        // Label/inspection window, not structural.
        translate([22, 18, -1])
            linear_extrude(height = plate_thickness + 2)
                slot_2d(32, 4);
    }
}

if (export_2d) {
    projection(cut = false) carrier_plate_3d();
} else {
    carrier_plate_3d();
}
