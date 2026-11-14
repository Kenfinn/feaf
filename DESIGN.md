# DESIGN.md: FEAF's visual direction

Read by the coding agent (anti-slop) before changing the look. FEAF's interface already
exists; new work follows this style and does not invent a new one.

## Who it is for

Retail investors and analysts in Taiwan, competition judges, and the team. They read numbers
and their sources. The screen must be information-dense, calm, and easy to match against the original document.

## Existing materials (use them, do not replace)

- Colors in `app/static/app.css` `:root`: `--navy` for the menu and primary buttons, `--naik`
  (up) red for rising prices, `--turun` (down) green for falling prices (Taiwan exchange convention),
  `--amber` for the held status or warnings, `--tolak` (reject) for failure, gray for secondary
  text.
- Fonts: Instrument Sans for text, IBM Plex Mono for numbers, stock codes, and data.
- Components: `.kartu` (card, a content block), `.kv` (a label and value row), `.cek` (a
  check row ✓/✕), `.lencana` (badge, status), `.pita` (banner, notification; `.fixture` yellow,
  `.nyata` (real) green, `.bahaya` (danger) red), `.tombol` (button), `.tombol.tipis` (thin), `.tombol.abu` (gray), the `.wl` table.
- Server-rendered Jinja2. No JavaScript framework, no build step, no new CDN.

## Rules

- Numbers are always right-aligned and use the mono font. Number formatting goes through the filters `rb` and `pct`
  (following the language).
- Every number that comes from an outside source has a link or source note near it.
- Statuses use the brief's state names: PUBLISHED, HELD, ARCHIVED.
- All text goes through `t()` in `app/i18n.py`, three languages.
- No gradients, heavy shadows, decorative icons, or animation. The only emoji are the 👍/👎 that
  are already in use.
- A new page copies the structure of existing pages: `.kepala` (header: kicker + title), then cards.
- The research disclaimer is shown as `.pita.fixture` on analysis pages.
