# Wireframe — Sentinel Saham

Eight lo-fi screens. Separate from `design/`, which holds the hi-fi version.

Live canvas: (private design canvas, not published)

## Why there are two versions

Hi-fi answers **"what does it look like"**. The wireframe answers **"why is it like that"**.

Each screen here has a numbered strip of notes beneath it. The notes are not labels
("this is a button") but reasons — why the fair value delta must be on the card, why the
risk profile must not be hidden on a Settings page, why a single verifier
rejection step is the most important element in the whole design.

It is used for two things:

1. **Team meetings.** Without color and typography, people argue about structure — and that is a
   useful argument. A finance team member can reject a layout without feeling they are
   criticising someone's taste.
2. **The 16 October document.** The first-stage assessment is a document review, not a system
   test. These numbered notes are the design rationale that cannot be read from a mockup.

## Contents

| File | Screen | Size |
|---|---|---|
| `Main.dc.html` | Alert feed | 1440×1040 |
| `DetailPeringatan.dc.html` | Detail + MOPS citation | 1440×840 |
| `Valuasi.dc.html` | DCF valuation | 1440×820 |
| `RiwayatNilaiWajar.dc.html` | Fair value history | 1440×900 |
| `TanyaJawab.dc.html` | Q&A | 1440×860 |
| `Watchlist.dc.html` | Watchlist & risk profile | 1440×780 |
| `JejakAudit.dc.html` | Agent audit trail | 1440×900 |
| `NotifPonsel.dc.html` | Phone notification | 390×1080 |

## Reading these wireframes

```
Gray box               content not yet decided — text, numbers, or data
Fully written text     sentences that really must read exactly like that
Orange circle          note marker, its number refers to the strip below
Dashed box             a container or link, not a solid element
```

The only color is the orange marker. That is deliberate: as soon as a wireframe has a palette,
the discussion drifts straight to color.

## What is deliberately left unanswered

Three things are in the canvas sticky notes and have not been drawn — the **empty state** (a day without
a single alert), the **error state** (MOPS cannot be reached), and **how long
history is kept**. All three need to be decided before the screens are built, not after.

## Rebuilding

The artboards are generated from Python scripts so that repeated patterns (text bars, zone boxes,
note strips) are not written out eight times:

```
python3 build_01_feed.py
python3 build_02_detail.py
python3 build_03_valuasi.py
python3 build_04_tanya_watchlist.py
python3 build_05_audit_ponsel.py
```

`build_common.py` holds the wrapper and the note-strip builder; `style_bersama.txt` holds
one style block that is inserted into every file.

Export for Figma and the deck:

```
node scripts/render_design.js wireframe
python3 scripts/build_figma_svg.py wireframe
```

Both are run from the repo root. The output is in `wireframe/export/` —
`Sentinel-Saham-wireframe.svg` is the file that is dragged into Figma.
