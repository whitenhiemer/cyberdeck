# Cyberdeck Build Roadmap

## Hardware

- **Brain:** Lenovo Legion Go (83E1, 8APU1)
- **Keyboard:** Planck (USB-C)
- **Hub:** MOKiN 13-in-1 USB-C docking station
- **Printers:** Ender 3 / Ender 5 (220x220mm bed)

## Design Spec

| Element | Decision |
|---|---|
| Form factor | Landscape slab |
| Integration | Non-destructive (Legion Go cradle) |
| Controllers | Detachable, re-attachable via side rails |
| Keyboard | Planck integrated, internal USB-C routing |
| Hub | MOKiN 13-in-1, ports exposed on right edge |
| Screen tilt | 10-15° wedge cradle |
| Back | Closed, structural rear wall |
| Dock placement | Rear wall cavity (ports → right edge cutouts) |
| Battery | OHOVIV 50000mAh, 3rd row, removable sliding bay (exits bottom edge) |
| Handle | Top bar (primary); recessed side grip (backup/iteration) |
| Aesthetic | Utilitarian / functional |

## Known Dimensions

| Component | Dimensions (mm) | Notes |
|---|---|---|
| Legion Go (with controllers) | 298.83 x 131 x 40.7 | 854g |
| Legion Go (base only) | 210 x 131 x 20.1 | 640g |
| Controller (each) | 44.8 x 136.7 x 42.25mm | 210g, own 900mAh battery |
| Controller width per side | ~44.4mm | matches (298.83 - 210) / 2 |
| Controller overhang (height) | +5.7mm over Go base | 136.7mm vs 131mm — protrudes top/bottom |
| Controller thickness overhang | +1.55mm over Go body | 42.25mm vs 40.7mm — bulges beyond Go profile |
| Controller connection | Pogo pins + physical rail | no electrical replication needed in chassis |
| Planck keyboard (V7) | 234 x 81 x 33mm | 510g assembled, 19mm key spacing |
| MOKiN dock | 130 x 55 x 15mm | built-in USB-C cable 6-8", ports on both long sides |
| OHOVIV 50000mAh power bank | 134 x 70 x 34mm | 613g, 22.5W, USB-C + 2x USB-A |

## Chassis Estimates

| Dimension | Value | Basis |
|---|---|---|
| Chassis width | ~305mm | Go full width + side walls |
| Chassis height | ~314mm | 131mm Go + ~93mm Planck + ~80mm battery + seams |
| Panel half width | ~150mm | fits 220mm bed |
| Back wall height (at 15°) | +35mm over front | tan(15°) × 131mm |
| Total weight (est.) | ~2.3kg | Go 854g + Planck 510g + bank 613g + chassis ~300g |

## Panel Layout

```
┌──────────[A]──────────┬──────────[B]──────────┐
│  controller rail (L)  │  controller rail (R)  │
│    [ Legion Go cradle (wedge, 10-15°) ]        │
├──────────[C]──────────┬──────────[D]───────────┤
│    [ Planck bay ]     │  [ dock bay ]          │
│                       │  (ports → right edge)  │
├──────────[E]──────────┴──────────[F]───────────┤
│       [ battery bay — slides out from bottom ] │
└────────────────────────────────────────────────┘
```

Side profile:
```
         ____________
        /  Go screen \  ← 10-15° tilt
       /   (20.1mm)  \
______/________________\______
[    Planck    ] [ dock  ]       ← flat base
```

## Phase 1 — Measurements & Dimensions

- [x] Legion Go body dimensions (base + with controllers)
- [x] Controller rail mechanism (slide top-to-bottom, latch at bottom — Joy-Con style)
- [ ] Controller rail groove profile (cross-section depth/width — requires calipers on Go side edge)
- [x] Planck keyboard outer dimensions (234 x 81 x 33mm with acrylic case)
- [x] MOKiN dock outer dimensions (130 x 55 x 15mm)
- [ ] Define final chassis outer dimensions
- [ ] Determine exact tilt angle (10-15°)
- [ ] Define panel split lines and fastener locations

## Phase 2 — CAD Design

- [x] Choose CAD tool (FreeCAD macros)
- [x] Model panel A — Go cradle top-left
- [x] Model panel B — Go cradle top-right
- [x] Model panel C — Planck bay bottom-left
- [x] Model panel D — dock bay bottom-right
- [ ] Model controller rail extensions (left + right)
- [x] Model rear wall / closed back
- [x] Add M3 heat insert holes and alignment pins at panel seams
- [x] Internal cable routing channels (Planck USB-C → dock)
- [ ] Model horizontal seam angle bracket clips (separate printed parts, 2 per seam × 2 seams = 4 total)
- [ ] Fit check / dry assembly review

## Phase 3 — Prototyping

- [ ] Print test pieces at panel seams (fit tolerances)
- [ ] Print controller rail mockup
- [ ] Adjust tolerances based on test prints
- [ ] Print full panels (likely 8-12 hour prints each)
- [ ] Dry fit all panels with hardware

## Phase 4 — Assembly

- [ ] Install M3 heat-set inserts
- [ ] Mount Legion Go in cradle
- [ ] Mount Planck in bay
- [ ] Mount dock in bay, route USB-C to Go
- [ ] Attach controller rails
- [ ] Final fit and finish (sanding, filler if needed)

## Phase 5 — Iteration

- [ ] Evaluate ergonomics (tilt angle, keyboard position)
- [ ] Evaluate top bar handle — if awkward, model recessed side grip variant
- [ ] Add any cable management details
- [ ] Consider paint / surface finish
- [ ] Document final design for reproducibility

## Notes

- All panel seams use M3 bolts + alignment pins
- Machine-specific local configs (Go firmware, etc.) never committed
- Controller rails: slide downward to remove — chassis side channels open at bottom
- Controllers are 5.7mm taller than Go base — top bar must clear controller tops
- Controller thickness (42.25mm) slightly exceeds Go body (40.7mm) — side channel needs clearance
- Pogo pins handle electrical connection — chassis only needs to replicate physical rail groove
- Rail groove cross-section still needs calipers before finalizing side panel CAD
- Battery bay slides out from bottom edge; USB-C port exposed via cutout, dock cable connects manually
- Battery bay retention: printed latch or M3 thumb screw
