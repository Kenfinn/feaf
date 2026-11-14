# UI Design — Sentinel Saham

Eight hi-fi screens for the Taiwan stock-monitoring agent, plus two diagrams
required by Appendix 1 as deck pages 5 and 6.

Both diagrams were deliberately drawn **before** the pipeline code was written: the state
diagram is the specification, not an illustration of the finished result. Drawing it forces answers to
what happens when an API fails, when the agent stops on its own, and when a human
is called in — questions that, if not answered here, only surface during the demo.

Live canvas: (private design canvas, not published)

## Contents

| File | Screen | Size |
|---|---|---|
| `Main.dc.html` | Alert feed | 1440×960 |
| `DetailPeringatan.dc.html` | Announcement detail + MOPS citation | 1440×960 |
| `Valuasi.dc.html` | DCF valuation, adjustable assumptions, sensitivity | 1440×1080 |
| `RiwayatNilaiWajar.dc.html` | Fair value history vs market price | 1440×980 |
| `TanyaJawab.dc.html` | Q&A — where the judges test | 1440×960 |
| `Watchlist.dc.html` | Watchlist & risk profile | 1440×900 |
| `JejakAudit.dc.html` | Agent audit trail | 1440×1000 |
| `NotifPonsel.dc.html` | Phone notification | 390×844 |
| `AlurState.dc.html` | **Agent task flow & states — deck page 5** | 1440×710 |
| `Arsitektur.dc.html` | **System architecture, model, tools — deck page 6** | 1440×820 |
| `canvas.json` | Canvas layout + sticky notes | — |

## Binding design decisions

**The numbers on the valuation screen are the real output of `scripts/dcf.py`** — EV 59,684 T, WACC 8.09%,
implied g 6.29%, and the entire sensitivity table. If the calculator changes, this screen
must be updated so it still matches when the judges check it against the worksheet.

**Red = up, green = down**, following the Taiwan exchange convention — the opposite of Western
exchanges. And red/green are used only for price movement; the valuation labels
(overvalued / fair / undervalued) use a neutral color so they are not confused with
price direction.

**Only one chart is built: fair value vs market price.** Not a candlestick — that
is in every brokerage app, cannot be cited, and proves nothing
about our agent. The fair value line is deliberately a staircase because it is only
recomputed when a new document arrives; each step can be clicked through to its MOPS document.

**The audit trail is a product screen, not a separate document.** In it there is one step
where the verifier rejects an alert draft because its number cannot be found in the source
document — that is the most direct evidence for the Safety, Controllability & Governance criterion.

**Spokesperson data is shown as removed.** The MOPS page contains a name, job title, and
phone number; the detail screen states explicitly that all three are not stored, in line with
Article 14.1 on personal data minimisation.

## Tokens

```
Navy    #16324F   structure, primary action
Amber   #A86A0B   attention (not danger)
Up      #C6362C   red — TW convention
Down    #17795E   green — TW convention
Ground  #EEF0F2   Surface #FFFFFF   Ink #101418
Typography: Instrument Sans (UI) + IBM Plex Mono (numbers)

Chart data series — NOT the UI colors above:
Fair value   #B5730C
Market price #2F74C0
```

Navy `#16324F` failed the test as a data series color (it reads as gray, chroma too low),
so the chart uses `#2F74C0` and `#B5730C` — this pair passes every
legibility check including a color-blindness simulation. Navy is still used for structure and buttons.

## Rebuilding the canvas

The file `sentinel-saham-aaic-2026.html` is deliberately not committed — it is 2.5 MB, and it can
be fully regenerated from the files in this folder through the `design` skill. Edit the `.dc.html`, re-seed,
then publish to the same URL.

## Figma status

The Figma connection has recovered. The file `Sentinel Saham — AAIC 2026` (key `ZTux17Ef8AZGb4yHUumizI`)
is still empty and waiting to be filled in as real layers.

Important note about the import format: the combined SVG file below embeds PNGs as
data URIs, so **all artboards enter Figma as flat images**, including both
diagrams. For the diagrams, editable layers are far more useful — a finance team member needs to
correct labels and arrows without going through a rebuild. That is done through the Figma MCP,
not through this SVG file.

## Export for Figma / deck

```
node scripts/render_design.js
```

Writes 2x PNGs to `design/export/`. This script waits for Instrument Sans and IBM Plex
Mono to be fully loaded before capturing — without that the result falls back to the system font and
the whole layout shifts.

```
python3 scripts/build_figma_svg.py
```

Combines all the PNGs into one `design/export/Sentinel-Saham-figma.svg`, arranged
according to `canvas.json`. **This is the file that is dragged into Figma** — in one import, the whole board
is formed, complete with the title of each screen.

`RiwayatNilaiWajar-chart.svg` is the chart only, extracted as a standalone SVG.
This is the only file that enters Figma as **real layers** — lines become
vector paths, axis numbers become editable text layers. The other PNGs enter as
flat images, not layers.

## English version

`design/en/` holds the English version of the ten files above, and its PNGs are in
`design/en/export/`. This version is the one used in Figma and the competition materials. Rebuild it after
changing the Indonesian-language screens:

```bash
python3 scripts/design_en.py          # translate → design/en/*.dc.html
node scripts/render_design.js design/en
```

New text that is not yet in the `EN` dictionary in `scripts/design_en.py` is reported when the script runs.
