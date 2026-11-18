# Changelog

## 1.3.3 · 18 Nov 2026

- Fix: every page still returned 500 after 1.3.2, now with `TypeError: unsupported operand
  type(s) for -: 'NoneType' and 'float'`. A clause-20 scenario replaces last year's capex with the
  amount in the filing; when that capex exceeds operating cash flow, FCFF0 is not positive and the
  reverse DCF has no meaningful answer (the implied growth comes out at or above WACC). The
  circularity check in `scripts/dcf.py` then computed `None - float`, the pipeline stopped, and
  every page that needs its results failed.
- `scripts/dcf.py`: when FCFF0 is not positive, `implied_growth`, the circularity values and the
  sensitivity grid (when there is no forward growth) are `None`/empty instead of raising. Positive
  FCFF0 gives exactly the same numbers as before.
- The post-calculation checker (`app/agent/verify.py`) fails closed: such a filing is held for
  review with the reason "free cash flow after this scenario is not positive", never published.
- `app/agent/pipeline.py`: an unexpected error in one filing no longer stops the run. That filing
  is held for review (`galat_proses`, cannot be approved as is) with the error in its trace, and the
  other filings are processed normally. Traces are written atomically.
- `app/agent/recompute.py`, `app/chat.py` and the valuation page handle an undefined implied growth.
- Tests: `tests/test_fcff_negatif.py` (9 tests; 7 fail on 1.3.2); 333 tests.

## 1.3.2 · 18 Nov 2026

- Fix: every page returned 500 on feaf.web.id. Two threads (the automatic pull and a page
  request) wrote the TWSE price cache through the same fixed `harga_twse.json.tmp`, leaving
  valid JSON followed by leftover bytes ("Extra data"). The side menu and the pipeline read that
  cache on every page and did not catch the error, and the cache was never fetched again
  because the read failed before the refetch step.
- Market caches (`app/pasar.py`): a corrupt cache file is now treated as missing, logged as
  `[pasar] cache <name> rusak, diabaikan`, fetched again and overwritten. The site recovers on
  its own; no manual cleanup of `/data/pasar/` is needed after deploying this version.
- JSON files are written through `app/berkas.py` (`tulis_json_atomik`), which gives each writer
  its own temporary file before `os.replace`. Used by the market caches, the filing store and
  pull status (`app/tarik.py`), and the triage thresholds (`app/umpan_balik.py`), which had the
  same fixed `.tmp` name.
- Tests: `tests/test_berkas_atomik.py` (11 tests: corrupt cache ignored and refetched, side menu
  and pipeline unaffected, concurrent writers leave valid JSON and no `.tmp`); 324 tests.

## 1.3.1 · 14 Nov 2026

- Privacy (PDPA data minimisation): raw OpenAPI snapshots in `DATA_DIR/raw/openapi/` are now
  written without the spokesperson fields listed in `PII_LABELS` (`tarik.tanpa_pii`), like the
  parsed data, traces and exports. Snapshots saved by older versions can be cleaned once with
  `python3 scripts/scrub_raw_snapshots.py` (also inside the Docker image).
- Tests: two new tests in `tests/test_agent.py` (raw snapshot without personal fields; the
  scrub script cleans old snapshots and is idempotent); 313 tests.

## 1.3.0 · 14 Nov 2026

- Page transitions (View Transitions API): the content area fades and slides between pages while
  the side menu and top bar stay in place. Browsers without the API navigate as before.
- Loading state: buttons that submit an action or refresh the data show a spinner in place of
  their icon and are locked until the page answers, so a double click cannot send twice.
- Ask FEAF panel slides in and out, and shows a typing indicator while an answer is prepared.
- Small interactions on cards, buttons, tabs, filters, folding sections, dropdowns and tooltips.
- Reduced motion: animations and transitions are switched off for visitors who ask for it
  (`prefers-reduced-motion`).
- Full-width layout: page content uses the whole window up to 1600 px on large screens, and the
  warning band follows the content width.
- README (four languages) now covers the AAIC 2026 Appendix 2 and safety rules in five new
  subsections: 9.6 operational metrics (tool-call success rate, retry count, termination rate,
  human intervention rate, error categories, an annotated operation trace), 9.7 safety test
  results, 10.3 data retention and deletion, 10.4 risk assessment, and 13.1 third-party
  resources. Known limitation 8 notes that data retention is manual.
- README: access-code guide (section 8.5); the Ask FEAF tool count is corrected to 13 (the
  `cari` name-search tool was missing from the list); the banner and two gallery pictures use
  the wide-screen screenshots.
- Internal working files, prompts and meeting material are git-ignored.
- All public documentation is in English: `docs/` files renamed to English names
  (`clause-mapping.md`, `security-report.md`, `attack-test-report.md`, `qa-report.md`,
  `evaluation-report.md`, `auto-valuation.md`, `data-access.md`, `flow-diagrams.md`,
  `third-party-disclosure.md`, `gold-set-results.md`, `gold-set-guide.md`,
  `pulling-mops-history.md`, `analysis-scope.md`) and translated, together with `DESIGN.md`,
  `design/README.md`, `wireframe/README.md` and the reports in `eval/hasil/`. The third-party
  disclosure adds Google Fonts and Swagger UI. The gold-set labelling sheet moved to
  `docs/gold-set/`. Internal planning notes are no longer published.
- Tests: 311.

## 1.2.0 · 14 Nov 2026

- English API paths: `/health`, `/check`, `/api/alerts`, `/api/traces/{id}`,
  `/api/valuation/{code}`, `/api/stocks/{code}/financials`, `/api/thresholds`, `/api/search`,
  `/api/ask`, `/api/ask/traces/{id}`, `/api/import`. The old Indonesian paths (`/sehat`,
  `/periksa`, `/api/peringatan`, `/api/jejak`, `/api/valuasi`, `/api/saham/.../keuangan`,
  `/api/ambang`, `/api/cari`, `/api/tanya`, `/api/impor`) stay as hidden aliases, so nothing
  breaks. JSON field names are unchanged.
- `/docs` (OpenAPI) is now in English and lists only the JSON API; HTML pages are hidden from it.
  API error messages are in English.
- `/docs` in three languages (`app/api_docs.py`): English by default, 繁體中文 via `?lang=zh`,
  Bahasa Indonesia via `?lang=id`, with a switcher on the page. Operations are grouped under seven
  tags, every parameter and request body is described, and handler docstrings no longer leak into
  the schema. `/redoc` is disabled.
- `POST /api/ask` accepts English body fields (`question`, `language`, `history`, `context`,
  `type`) next to the old ones; `POST /api/import` accepts header `X-Access-Code` next to
  `X-Kode-Akses`.
- Pages, `chat.js`, `ui.js`, the Docker health check and `scripts/kirim_riwayat.py` use the new
  paths.
- README rewritten (architecture diagrams, API reference with examples, tech stack) in English,
  with translations in 繁體中文 (`README.zh-TW.md`), Bahasa Indonesia (`README.id.md`) and
  Tiếng Việt (`README.vi.md`).
- Tests: `tests/test_api_inggris.py` (new paths, legacy aliases, English OpenAPI) and
  `tests/test_api_docs.py` (three-language `/docs`); 307 tests.

## 1.1.0 · 13 Nov 2026

- Ask FEAF slide-over panel on every page (`_panel_chat.html`, `app/static/chat.js`,
  `app/static/chat.css`) with page-aware suggestion chips and `sessionStorage` conversation
  persistence across pages.
- Multi-turn chat API (`POST /api/tanya` accepting `riwayat` and `konteks`) with 32-hex
  HMAC-SHA256 signing (`tanda(id, jawaban)` via `SENTINEL_CHAT_RAHASIA`); unsigned or altered
  assistant turns and injected user turns are dropped and logged in the trace.
- Follow-up question resolution without repeating the stock code (from question, page context,
  last verified turn, or announcement prefix) and conversation **Recap** (`recap` /
  `recap_template` verified against signed assistant turns).
- Six read-only menu tools (`feed`, `peringatan`, `jejak`, `review`, `ambang`, `watchlist`)
  alongside the six stock tools, with internal navigation links (`tautan`) and zero PII / zero
  file mutation.
- Multi-turn chat evaluation (`eval/chat_percakapan.csv`, `scripts/evaluasi.py --chat-percakapan`:
  36/36 turns and 12/12 scenarios in three languages on the rule path) and 7 mandatory
  conversation security tests (`tests/test_chat_percakapan.py`).
- UI and accessibility refinements across feed, stock detail, alert detail, valuation, review,
  thresholds, watchlist, trace, and plain-language hold reasons.
- QA hardening: offline MOPS citation fallback on empty financials, `[hidden]` CSS visibility
  guarantee, standalone `401` lock page (`POST /akses` + signed access cookie), thread-safe chat
  worker offloading and LLM/review locking, word-boundary narration checker, watchlist cached
  prices, and localized fallback trace labels.

## 1.0.0 · 12 Nov 2026 · finalist package (AAIC 2026)

The version submitted with the finalist package. Evaluation numbers in the README and
`docs/laporan-evaluasi.md` were measured on this code line.

- Agent pipeline: clause screen → triage → extraction (Gemini 3.6 Flash, rule-based fallback)
  → deterministic recompute → deterministic checker. Lanes for valuation, risk, capital,
  quarterly report, severe and governance clauses.
- Automatic DCF for non-financial issuers, built for every issuer whose filing needs it.
- Ask FEAF chat page: answers only from tools, every number checked, advice refused.
- Review queue, 👍/👎 thresholds, watchlist, stock pages with six tabs, three languages.
- Evaluation: gold set (46 filings), attack set (72 cases), chat set (52 questions),
  operations report, reproducible offline from `eval/gold_dokumen.json`.
