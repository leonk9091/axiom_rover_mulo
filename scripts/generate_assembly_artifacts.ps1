param(
    [switch]$SkipFreeCAD
)

$ErrorActionPreference = "Stop"

$repo = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$ws = Join-Path $repo "axiom_rover_ws"
$rex = Join-Path $ws "hardware\electronics\rex_controller"
$generated = Join-Path $rex "generated"
$kicadOut = Join-Path $generated "kicad"
$graphOut = Join-Path $generated "graphs"
$wireOut = Join-Path $generated "wireviz"
$mech = Join-Path $ws "hardware\mechanical\rex_controller_carrier"
$mechOut = Join-Path $mech "generated"

New-Item -ItemType Directory -Force -Path $kicadOut, $graphOut, $wireOut, $mechOut | Out-Null

function Resolve-Tool($name, [string[]]$candidates) {
    foreach ($candidate in $candidates) {
        if ($candidate -and (Test-Path $candidate)) {
            return $candidate
        }
    }
    $cmd = Get-Command $name -ErrorAction SilentlyContinue
    if ($cmd) {
        return $cmd.Source
    }
    return $null
}

$kicad = Resolve-Tool "kicad-cli" @(
    "C:\Program Files\KiCad\10.0\bin\kicad-cli.exe",
    "C:\Program Files\KiCad\9.0\bin\kicad-cli.exe"
)
$openscad = Resolve-Tool "openscad" @("C:\Program Files\OpenSCAD\openscad.exe")
$freecad = Resolve-Tool "freecadcmd" @(
    "$env:LOCALAPPDATA\Programs\FreeCAD 1.1\bin\freecadcmd.exe",
    "C:\Program Files\FreeCAD 1.0\bin\freecadcmd.exe"
)
$dot = Resolve-Tool "dot" @()
$wireviz = Resolve-Tool "wireviz" @()

if (-not $dot) { throw "Graphviz dot not found" }
if (-not $wireviz) { throw "WireViz not found" }
if (-not $kicad) { throw "KiCad CLI not found" }
if (-not $openscad) { throw "OpenSCAD not found" }

$dotSource = Join-Path $rex "rex_power_architecture.dot"
& $dot -Tpng $dotSource -o (Join-Path $graphOut "rex_power_architecture.png")
& $dot -Tsvg $dotSource -o (Join-Path $graphOut "rex_power_architecture.svg")
& $dot -Tpdf $dotSource -o (Join-Path $graphOut "rex_power_architecture.pdf")

$wireSource = Join-Path $rex "wireviz\rex_controller_harness.yml"
& $wireviz -f hpst -o $wireOut -O "rex_controller_harness" $wireSource

$sch = Join-Path $rex "kicad\mulo_rex_controller\mulo_rex_controller.kicad_sch"
& $kicad sch export svg --exclude-drawing-sheet --black-and-white -o $kicadOut $sch
& $kicad sch export pdf --exclude-drawing-sheet --black-and-white -o (Join-Path $kicadOut "mulo_rex_controller.pdf") $sch
& $kicad sch erc --output (Join-Path $kicadOut "mulo_rex_controller_erc.rpt") $sch

$scad = Join-Path $mech "rex_controller_carrier_plate.scad"
& $openscad -o (Join-Path $mechOut "rex_controller_carrier_plate.stl") $scad
& $openscad -D "export_2d=true" -o (Join-Path $mechOut "rex_controller_carrier_plate.dxf") $scad
& $openscad --imgsize=1400,900 --viewall --autocenter -o (Join-Path $mechOut "rex_controller_carrier_plate.png") $scad

if (-not $SkipFreeCAD -and $freecad) {
    & $freecad (Join-Path $mech "freecad_rex_controller_carrier.py")
}

Write-Output "Assembly artifacts generated in:"
Write-Output "  $generated"
Write-Output "  $mechOut"
