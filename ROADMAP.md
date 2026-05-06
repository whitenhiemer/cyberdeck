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
| Aesthetic | Utilitarian / functional |

## Panel Layout

```
┌──────────[A]──────────┬──────────[B]──────────┐
│  controller rail (L)  │  controller rail (R)  │
│    [ Legion Go cradle (wedge, 10-15°) ]        │
├──────────[C]──────────┬──────────[D]───────────┤
│    [ Planck bay ]     │  [ dock bay ]          │
│                       │  (ports → right edge)  │
└───────────────────────┴────────────────────────┘
```

Side profile:
```
         ____________
        /  Go screen \  ← 10-15° tilt
       /   (38mm deep)\
______/________________\______
[    Planck    ] [ dock  ]       ← flat base
```

## Phase 1 — Measurements & Dimensions

- [ ] Measure Legion Go body precisely (without controllers)
- [ ] Measure controller rail dimensions and attachment mechanism
- [ ] Measure Planck keyboard (PCB + case)
- [ ] Measure MOKiN dock body
- [ ] Define final chassis outer dimensions
- [ ] Determine exact tilt angle (10-15°)
- [ ] Define panel split lines and fastener locations

## Phase 2 — CAD Design

- [ ] Choose CAD tool (FreeCAD / OpenSCAD / Fusion 360)
- [ ] Model panel A — Go cradle top-left
- [ ] Model panel B — Go cradle top-right
- [ ] Model panel C — Planck bay bottom-left
- [ ] Model panel D — dock bay bottom-right
- [ ] Model controller rail extensions (left + right)
- [ ] Model rear wall / closed back
- [ ] Add M3 bolt holes and alignment pins at panel seams
- [ ] Internal cable routing channels (Planck USB-C → dock)
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
- [ ] Add any cable management details
- [ ] Consider paint / surface finish
- [ ] Document final design for reproducibility

## Notes

- All panel seams use M3 bolts + alignment pins
- Machine-specific local configs (Go firmware, etc.) never committed
- Controller rails must replicate Go's native slide mechanism — verify exact rail dimensions before CAD
