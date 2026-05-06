# Cyberdeck

A 3D-printed chassis that turns a Lenovo Legion Go into a portable cyberdeck workstation. Non-destructive — the Go sits in a cradle and can be removed.

## Hardware

| Component | Model | Dimensions |
|---|---|---|
| Brain | Lenovo Legion Go (83E1, 8APU1) | 298.83 x 131 x 40.7mm (with controllers) |
| Keyboard | Planck V7 (USB-C) | 234 x 81 x 33mm |
| Hub | MOKiN 13-in-1 USB-C dock | 130 x 55 x 15mm |
| Battery | OHOVIV 50000mAh power bank | 134 x 70 x 34mm |
| Printers | Ender 3 / Ender 5 | 220x220mm bed |

## Design

- **Form:** Landscape slab, three horizontal rows
- **Tilt:** 15° wedge cradle for the Go (screen angles toward user)
- **Controllers:** Detachable — chassis side channels open at bottom for slide-out removal
- **Back:** Closed rear wall with open vent cutout behind Go exhaust; 5mm kickstand clearance gap
- **Battery:** Removable sliding bay, exits from bottom edge

```
┌──────────[A]──────────┬──────────[B]──────────┐  ← Go cradle (62mm tall)
│  controller rail (L)  │  controller rail (R)  │
│    [ Legion Go cradle — 15° wedge ]            │
├──────────[C]──────────┬──────────[D]───────────┤  ← Planck + dock (36mm tall)
│    [ Planck bay ]     │  [ dock bay ]          │
├──────────[E]──────────┴──────────[F]───────────┤  ← Battery (40mm tall)
│       [ battery bay — slides out from bottom ] │
└────────────────────────────────────────────────┘
  Total: 305 x 138mm face, ~314mm front-to-back
```

## CAD

FreeCAD Python macros in `cad/`. Each panel is a standalone script — open FreeCAD, run the macro via **Macro → Macros**, and it generates and saves the `.FCStd` file.

| File | Description |
|---|---|
| `panel_a.py` | Go cradle, left half — wedge cavity + left controller channel |
| `panel_b.py` | Go cradle, right half — wedge cavity + right controller channel |
| `panel_c.py` | Planck bay, left half |
| `panel_d.py` | Planck bay, right half (dock bay on right) |
| `panel_e.py` | Battery bay, left half |
| `panel_f.py` | Battery bay, right half (USB-C port cutout) |
| `rear_wall.py` | Rear structural wall with Go exhaust vent cutout |

All panels use M3 bolts + alignment pins at seams (holes TBD once final dimensions are locked).

## Open Items

- [ ] Controller rail groove cross-section — needs calipers on Go side edge
- [ ] Final chassis outer dimensions
- [ ] Panel split lines and fastener locations
- [ ] Model controller rail extensions (left + right)
- [ ] Add M3 bolt holes and alignment pins at seams
- [ ] Internal cable routing (Planck USB-C → dock)

## Reference Photos

`photos/` — Legion Go back face, side rail profile, controller connection end.
