# Comprehensive QA Report — FEAF (AAIC 2026)

- **Initial audit date**: 2026-11-13 (baseline commit `ca04367` + working changes in `app/main.py`, `app/store.py`, `tests/test_valuasi_otomatis.py`)
- **Post-fix verification date**: 2026-11-13
- **Readiness conclusion**: **Ready for release/submission from the code and testing side** — all Critical (`K-1`), High (`T-1`, `T-2`), Medium (`M-1` to `M-6`) findings, and the de-identification/version/Git and Docker ignore blockers in Section 4, have been fixed and verified as passing (`293` unit tests on both local data and a clean `SENTINEL_DATA_DIR`, `84/84` page QA with no warnings, responsive QA `0` findings, evaluation and attack tests passing, and interactive Playwright Chrome verification for `T-1`, `M-1`, and `T-2`). What remains is only low-priority notes (`R-1` to `R-3`, optional) and leaving out the untracked local files (including `"API KEY .txt"`) if a manual submission archive is made outside `git`.

---

## 1. Execution Limits & Scope

Testing was done in an environment without model API keys (`SENTINEL_API_KEY` and `GEMINI_API_KEY` empty):

1. All pipeline and chatbot evaluations ran on the **rule reasoner + deterministic template** path (`--tanpa-model`, i.e. without model), not direct calls to the Gemini API.
2. HTML and interactive browser checks were run through `FastAPI TestClient` and **Playwright headless Google Chrome** against an isolated copy of `data/` and an empty `SENTINEL_DATA_DIR` (with `SENTINEL_SERTAKAN_CONTOH=1`).
3. A direct integration test of `POST /api/impor` against an external live server and a full Docker image build test were not run in this session (`docker` CLI `29.1.3` installed).

---

## 2. Automated Test Result Matrix (Post-Fix)

| Check | Scope & Conditions | Result | Result Details |
|---|---|---|---|
| **Unit tests (local data)** | `python3 -m unittest discover -s tests -v` | **Pass** | `Ran 293 tests in 6.946s`, `OK` (includes 14 new regression tests in `tests/test_qa_perbaikan.py`) |
| **Unit tests (clean data)** | empty `SENTINEL_DATA_DIR` | **Pass** | `Ran 293 tests in 11.859s`, `OK` |
| **Bytecode compilation** | `python3 -m compileall -q app scripts tests` | **Pass** | Exit code `0` |
| **Gold + Fixture evaluation** | `scripts/evaluasi.py` (50 labeled documents: fixtures + 46 `eval/gold_dokumen.json`) | **Pass** | `0/50 (0%)` wrong figures (`tanpa-pemeriksa` (without checker): `4/50 (8%)`); `49/50 (98%)` publish/not; `46/50 (92%)` 3-way decision (`4749-2026-11-09-172344` held, 3 `arsip` (archived) held); input field accuracy `2/2 (100%)` & value `2/2 (100%)`; moderate signal rate `29/29 (100%)` |
| **Operational evaluation** | `scripts/evaluasi.py --operasional` (4 fixtures) | **Pass** | 3 passed the clause filter: `2` `PUBLISHED`, `1` `HELD` (`tahan.verifikasi:cek.besaran+cek.konversi+cek.mu`), `1` `ARCHIVED` (`arsip.saringan_pasal`), latency `0/0/0/0 ms`; interventions `1` (`25.0%` of total / `33.3%` of those that passed the filter) |
| **Deterministic attack test** | `scripts/uji_serangan.py` (threshold `0.40`) | **Pass** | `72` scenarios, **`0` `terbit_salah`** (wrongly published) |
| **Ask FEAF (`--chat`)** | `scripts/evaluasi.py --chat` | **Pass** | `52/52 (100%)` total (`25/25` sourced, `27/27` refused), `0` recommendation words passed |
| **Ask FEAF Multi-Turn** | `scripts/evaluasi.py --chat-percakapan` | **Pass** | `36/36 (100%)` turns, `12/12` scenarios, `0` recommendation words passed |
| **Playwright Responsive QA** | `scripts/qa_responsif.py --lebar 390 768 1024 1440` | **Pass** | `15 routes x 3 languages x 4 widths = 0 findings` |
| **Page QA (local `data/`)** | `scripts/qa_halaman.py --verbose` | **Pass** | `84/84` combinations passed (`Gagal: 0`; `Gagal` = failed), `0` warnings |
| **Page QA (clean `DATA_DIR`)** | empty `SENTINEL_DATA_DIR` + `SENTINEL_SERTAKAN_CONTOH=1` | **Pass** | `84/84` combinations passed (`Gagal: 0`), `0` warnings |
| **i18n dictionary (`app.i18n._T`)** | Python inspection after the edit | **Pass** | `887` valid keys (grew by `jj.sebab.tanpa_kunci`) |
| **De-identification test & grep** | `tests.test_deidentifikasi` + `rg -in` | **Pass** | `1` test (`0.027s`, `OK`; now scans `eval/` including `.csv`); `rg` over `README.md`, `eval/`, `app/` = `0` matches |

### Interactive Playwright Verification & Security Testing

- **Post-fix interactive verification (`T-1`, `M-1`, `T-2` via Playwright Chrome)**:
  - **`T-1` (`/`, 1 mixed `.kelompok-tanggal`)**: initially the `dilewati` (skipped) rows were hidden (`hidden=True`, `display="none"`, `offsetHeight=0`); clicking the `terbit` (published) and `ditahan` (held) filters showed only the rows matching the status (`display="flex"`, `offsetHeight > 0`) and hid the other rows (`display="none"`, `offsetHeight=0`) without horizontal overflow.
  - **`M-1` (`/review`)**: the `"Semua"` (All) chip uses `.chip.on` (`rgb(22, 50, 79)`), and when the `"verifikasi"` chip is clicked, the navy background moves to `"verifikasi"` while `"Semua"` returns to normal (`rgb(255, 255, 255)`).
  - **`T-2` (`SENTINEL_KUNCI_BACA=1`, `SENTINEL_KODE_AKSES=rahasia-qa`)**: `GET /` replies `401` without `.rail`, `cp-panel`, or `"2330"`; `POST /akses` with a wrong code returns `303` to `GET /?pesan=...` (`401`) with a `.pita.err` banner without leaking the code in the URL; `POST /akses` with the right code opens access (`303` -> `200`, sidebar `.rail` & `"2330"` shown) and sets the `akses` cookie to a 64-character hex HMAC digest (`!= "rahasia-qa"`).
- **Initial baseline Playwright & security verification (pre-fix)**:
  - **Ask FEAF flow (`#cp-panel` & `/tanya`)**: clicking `#cp-fab` opens the panel; clicking a suggestion chip fills `.cp-daftar`; sending a follow-up question updates `sessionStorage` (`feaf_chat`, `feaf_chat_buka="1"`); navigating to `/watchlist` keeps the panel open and the history intact; the `Recap` (`.cp-aksi-recap`) and `New` (`.cp-aksi-baru`) buttons work as designed; submitting the `POST /tanya` form redirects to `/tanya?id=...` and shows the `2330` result.
  - **Navigation & Phone Drawer (`390×844`)**: horizontal overflow `0px` on `/`, `/saham/2330`, `/saham/2330?tab=keu`, `/saham?kode=台`, `/saham?kode=Corp`, `/review`, `/watchlist`, `/valuasi/2330`, `/tanya`; the phone menu button adds `body.laci-terbuka`.
  - **Autocomplete & Language**: typing `"233"` in `input[data-cari-saran]` brings up 8 `.daftar-saran` suggestions (`hidden: false`, `display: block`); clicking the `/bahasa/zh` link changes the `h1` to `警示` and sets the cookie `bahasa=zh`.
  - **Browser Console Log**: `0` uncaught `pageerror`, but 1 `console.error` (`404 Not Found`) appears in every new session because `GET /favicon.ico` is not served yet (see `R-3`).
  - **Authentication & Open Redirect**: when `SENTINEL_KODE_AKSES` is set and `KUNCI_BACA=0`, mutations (`POST /review/*`, `POST /umpan-balik/*`, `POST /ambang/*`, `POST /periksa`, `POST /watchlist/*`, `GET /ekspor/kandidat-gold.csv`, `POST /api/impor`) return `303`/`403`; the redirects `?lanjut=//evil.example/x` and `?kembali=https://evil.example/x` are safely held back to `/` or `/watchlist`.
  - **Auto-Valuation (`data/valuasi_otomatis/`)**: `store.emiten_tervaluasi()` returns `40` issuers; samples `/valuasi/{1216,1303,1467,1560,1586}` & `/api/valuasi/...` return `200`, non-eligible issuers (`/valuasi/{1301,1525}`) return `404`.

---

## 3. List of Verified Bugs & Gaps

### Critical Priority

#### K-1. `HTTP 500` crash on `/saham/{kode}?tab=keu` when financial data is unavailable — **Status: Fixed**
- **Location**: `app/templates/saham.html:249-258`, `app/sitasi.py` (`mops_laporan`, `mops_cadangan`)
- **Symptom & Root Cause (initial audit)**:
  When the financial statement table is not yet available (`tb.ada == False`), `saham.html:255` renders the fallback link by calling `mops_laporan(kode_saham, None, None, lap)`. In `app/sitasi.py`, the `else` branch runs `th = int(str(tahun_iso)[:4])`, so `tahun_iso=None` raises `ValueError: invalid literal for int() with base 10: 'None'`, even though `mops_cadangan` already exists.
- **Fix & Verification**:
  `app/templates/saham.html:255` was changed to call `mops_cadangan(lap)`, and `app/sitasi.py` `mops_laporan()` now guards the `tahun_iso` value (`None`, empty, `"None"`, or non-numeric) so that it falls straight through to `mops_cadangan(laporan)`. Verified through `scripts/qa_halaman.py` on an empty `SENTINEL_DATA_DIR` (`84/84`, `0` failed) and `tests/test_qa_perbaikan.py` (`TestSitasiFallback`).

---

### High Priority

#### T-1. Status & type filters in the `/` Feed do not hide rows in a mixed-date group — **Status: Fixed**
- **Location**: `app/static/app.css:48`, `app/static/ui.js:73-78`
- **Symptom & Root Cause (initial audit)**:
  `ui.js:73` hides rows with `b.hidden = !ok;`, but `app/static/app.css` declares `.baris { display: flex; ... }` without a global `[hidden] { display: none !important; }` rule, so when one date has mixed statuses, a row with `[hidden]` is still shown as `display: flex`.
- **Fix & Verification**:
  Added the global rule `[hidden] { display: none !important; }` at `app/static/app.css:48`. Verified by the regression test `TestCssDanUiReview.test_css_memiliki_aturan_hidden_global` and an interactive Playwright Chromium test on a mixed `.kelompok-tanggal` group (`terbit`, `ditahan`, `dilewati` filtered cleanly with `display: "none"` and `offsetHeight: 0`).

#### T-2. The `HTTP 401` response in locked-read mode leaks the watchlist & sidebar, and the `akses` cookie is too weak — **Status: Fixed**
- **Location**: `app/main.py` (`_token_akses`, `_baca_pesan`, `_konteks_kunci`, `_boleh_ubah`, `kunci_baca_middleware`, `_proses_akses`, `akses`, `akses_post`), `app/templates/kunci.html`
- **Symptom & Root Cause (initial audit)**:
  In `SENTINEL_KUNCI_BACA=1` mode, the `401` response calls the full `konteks()`, so the `401` HTML still carries the sidebar, `#cp-panel`, and the watchlist stock codes; in addition, `POST /akses` returned `405` and the `akses` cookie stored the raw `config.KODE_AKSES`.
- **Fix & Verification**:
  1. `app/templates/kunci.html` was changed into a minimal standalone page (not inheriting `base.html`) using `_konteks_kunci()`, so the `401` response contains no `.rail`, `#cp-panel`, or watchlist data.
  2. Supports `POST /akses` (`@app.post("/akses")`) together with a `method="post"` form in `kunci.html`, and replaces the `akses` cookie value with an HMAC-SHA256 digest via `_token_akses()` verified with `hmac.compare_digest()`.
  Verified through `TestR3KunciBaca` (`tests/test_putaran2.py`), `TestKunciBacaKeamanan` (`tests/test_qa_perbaikan.py`), and the full Playwright flow (GET `401` clean, wrong POST -> `303`/`401` `.pita.err`, correct POST -> `200` + 64-character hex HMAC cookie).

---

### Medium Priority

#### M-1. The `"Semua"` filter chip in `/review` stays active, lit twice — **Status: Fixed**
- **Location**: `app/templates/review.html:29`, `app/static/app.css`, `app/static/ui.js:156-160`
- **Symptom & Root Cause (initial audit)**:
  `review.html:29` uses `class="chip aktif"`, while `ui.js:156-160` only toggles `.on`, so the `"Semua"` button keeps a navy background even when another chip is selected.
- **Fix & Verification**:
  Changed `class="chip aktif"` to `class="chip on"` in `app/templates/review.html:29`. Verified through `TestCssDanUiReview` and an interactive Playwright Chrome click on `/review` (the `"Semua"` chip drops the `rgb(22, 50, 79)` background to white when `"verifikasi"` is selected).

#### M-2. The chatbot `async def` handlers block the event loop & mutate globals/cache without safe locking — **Status: Fixed**
- **Location**: `app/chat.py` (`kirim_tanya`, `api_tanya`, calling `llm.tandai_404`), `app/agent/llm.py` (`_kunci_model`, `_lokal`, `tandai_404`, `_tanya_model`, `_tulis_cache`), `app/review.py` (`_kunci_berkas`, `simpan`)
- **Symptom & Root Cause (initial audit)**:
  `kirim_tanya` and `api_tanya` call `tanya()` (synchronous network I/O + sleep) directly on the `async def` event loop; the model fallback writes the global variable `_model_sementara` without thread isolation; and cache/review writes use a static `.tmp` file without a concurrency lock.
- **Fix & Verification**:
  1. `kirim_tanya` and `api_tanya` now run `await asyncio.to_thread(tanya, ...)`.
  2. `app/agent/llm.py` uses `_kunci_model = threading.RLock()`, `_lokal = threading.local()` for `model_sementara`, a `tandai_404(model)` function, and a unique PID+TID temporary file in `_tulis_cache` while keeping the `model_dipakai()` and `_panggil_gemini(instruksi, dokumen)` API compatible.
  3. `app/review.py` uses `_kunci_berkas = threading.Lock()` and a unique PID+TID temporary file in `simpan()`.
  Verified through `TestKonkurensiDanPemeriksa` (a `review.simpan` test with 16 threads, `llm._tulis_cache` with 12 threads, worker-thread verification on `POST /api/tanya`) and `tests/test_agent.py` & `tests/test_pemutus_thread.py`.

#### M-3. The forbidden-word checker in `ringkasan.py` wrongly blocks neutral words — **Status: Fixed**
- **Location**: `app/ringkasan.py` (`_muat_kata_terlarang`, `periksa_narasi`)
- **Symptom & Root Cause (initial audit)**:
  The substring match `k.lower() in teks.lower()` blocks neutral words such as `pembelian` (purchase), `buyback`, and `selling`.
- **Fix & Verification**:
  Extracted `_muat_kata_terlarang()` using an ASCII word-boundary regex with neutral exceptions for `buyback`/`beli kembali` (buy back), aligned with `chat.TERLARANG`, while keeping the CJK word check and the `KATA_TERLARANG` list. Verified through `TestKonkurensiDanPemeriksa.test_ringkasan_izinkan_buyback_dan_pembelian`.

#### M-4. The price column in `/watchlist` always shows `—` — **Status: Fixed**
- **Location**: `app/main.py` (`watchlist`), `app/templates/watchlist.html:68-77`
- **Symptom & Root Cause (initial audit)**:
  The `watchlist()` handler does not fill the `"harga"` (price) key, so the `watchlist.html` template always shows `—`.
- **Fix & Verification**:
  `watchlist()` in `app/main.py` now fills `"harga": harga_cache.get("tutup")` from one `pasar.harga_dari_cache(k)` call per issuer. Verified through `TestTampilanDanCookie.test_watchlist_memuat_harga_cache`.

#### M-5. The fallback reason label `"tidak ada kunci API"` leaks in Indonesian into the EN/ZH UI — **Status: Fixed**
- **Location**: `app/i18n.py` (`jj.sebab.tanpa_kunci`), `app/main.py` (Jinja filter `sebab_bahasa`), `app/templates/jejak.html:54`, `scripts/qa_halaman.py`
- **Symptom & Root Cause (initial audit)**:
  The raw string `"tidak ada kunci API"` ("no API key") appears directly on `/jejak/{id}?bahasa=en` and `zh`, triggering the Indonesian-word leak warning in `scripts/qa_halaman.py`.
- **Fix & Verification**:
  Added the key `"jj.sebab.tanpa_kunci"` in `app/i18n.py` (`"no API key set"` / `"未設定 API 金鑰"` / `"tidak ada kunci API"`), registered the `sebab_bahasa` filter in `app/main.py`, and applied it at `app/templates/jejak.html:54` (without changing the JSON payload of `/api/jejak/{id}`); also tightened `scripts/qa_halaman.py` so that the Indonesian-word leak scan on HTML only runs when `content-type` is HTML. `qa_halaman.py` result: `84/84` with `0` warnings.

#### M-6. Template inconsistencies, duplicate badge, `0` values, & risk-profile cookie — **Status: Fixed**
- **Header & table wrapper of `cari_hasil.html`**: `app/templates/cari_hasil.html` now wraps the table in `<div class="tabel-geser">`, uses `{{ t('pf.en') }}` and `{{ t('pf.bursa') }}`, and replaces the undefined `var(--latar-2)` with `var(--netral-100)`.
- **`HELD` badge in `/review`**: the duplicate pill `<span class="lencana l-dilewati mono">HELD</span>` at `app/templates/review.html:50-53` was replaced with a dimmed mono meta label so that it is not a double badge while still keeping the status text `"HELD"` per the `tests/test_agent.py` contract.
- **Financial value `0` in `saham.html`**: `app/templates/saham.html:165, 175-176` was changed to an explicit `is not none` check so that the figure `0` is still displayed.
- **Inconsistent `risiko` cookie**: a shared helper `_simpan_cookie_risiko()` was added in `app/main.py` to store the `?risiko=` choice in a cookie on the `/ambang` and `/valuasi/{kode}` routes (correction note to the initial finding: the `/peringatan/{pengenal}` route actually already set the `risiko` cookie, whereas those that did not were `/ambang` and `/valuasi/{kode}`). Verified through `TestCssDanUiReview` and `TestTampilanDanCookie`.

---

### Low Priority & Design Notes

#### R-1. The `POST /api/tanya` and `POST /tanya` endpoints are open when `KUNCI_BACA=0` — **Status: Standing Note (Low Priority)**
- **Location**: `app/chat.py` (`kirim_tanya`, `api_tanya`)
- **Note**: When `SENTINEL_KODE_AKSES` is set with `KUNCI_BACA=0`, all data mutations are locked, but `POST /api/tanya` (`200`) and `POST /tanya` (`303`) can still be called publicly without the access cookie (although limited by `MAX_PER_HOUR=60` for Gemini model calls and writing to `DATA_DIR/traces_chat/`). Document this behavior or restrict it too if the API quota should be kept tight.

#### R-2. Chat history is truncated to 1500 characters before the HMAC is re-verified — **Status: Standing Note (Low Priority)**
- **Location**: `app/chat.py` (`_bersihkan_riwayat`, `_teks_asisten_sah`)
- **Note**: `_bersihkan_riwayat` verifies the HMAC against `teks_asli`, then stores the truncated version `teks = teks_asli.strip()[:1500]`. If an assistant answer ever exceeds 1500 characters, the repeated HMAC check in `_teks_asisten_sah` against the truncated `teks` will fail and discard the reference figures of that turn.

#### R-3. Console `404` because `/favicon.ico` is not available — **Status: Standing Note (Low Priority)**
- **Location**: `app/templates/base.html`, `app/main.py`
- **Note**: Every new session opened in Chrome/Playwright produces 1 console error `404 Not Found` for `/favicon.ico`. Optionally add a lightweight SVG data-URI `<link rel="icon" ...>` in `base.html` or a `/favicon.ico` route.

---

## 4. Release Hygiene & De-identification Findings (Submission Blockers)

1. **De-identification outside `app/` — Status: Fixed**:
   - All `46` lines containing annotator initials in `eval/gold.csv` were replaced with `,Analis 1,`.
   - `tests/test_deidentifikasi.py` was extended to also scan the `eval/` folder (including `.csv`).
   - GitHub repository URLs containing a team member's username in `README.md` (lines `31`, `60`, and `89`) were neutralized to `<repository-url> napaincu-ai-comp`.
   - Verification with `rg -in` using patterns of team member names, GitHub usernames, and annotator initials over `README.md eval/ app/` gives `0` matches.
2. **API key file & untracked local artifacts in the root — Status: Secured via `.gitignore` / `.dockerignore` (files kept on disk)**:
   - `"API KEY .txt"` and `scripts/result.json` were added to `.gitignore` and `.dockerignore` so they are not committed or pulled into the Docker build context.
   - Per the work request/constraints, `"API KEY .txt"` and the other untracked local files (`Panduan-Gold-Set-FEAF.pdf`, `Rapat-Perdana-AAIC-2026.pdf`, `Rapat-Perdana-AAIC-2026.pptx`, `gold-set-FEAF.xlsx`, `gold-set-FEAF(1).xlsx`, `scripts/result.json`, `.agents/`, `skills-lock.json`, `docs/feaf_snapshot/`, `docs/draf-slide-tambahan.md`) were **not deleted from disk**; make sure those files are not packaged if a `.zip`/tarball archive is made manually outside `git`.
3. **Version & unit test count synchronization — Status: Fixed**:
   - `app/versi.py`, `CHANGELOG.md`, and `README.md` were synchronized to version `1.1.0`.
   - `README.md:149` was updated to `293 tests` per the result of `unittest discover -s tests -v`.

---

## 5. Follow-Up Status Summary

1. **Done (`K-1`, `T-1`, `T-2`, `M-1` to `M-6`, Section 4)**: all verified bugs and code/de-identification blockers have been fixed, plus 14 regression tests in `tests/test_qa_perbaikan.py`, and passed full verification (`293` unit tests on both local data and an empty `SENTINEL_DATA_DIR`, `qa_halaman.py` `84/84` with `0` warnings in both conditions, `qa_responsif.py` `0` findings, `evaluasi.py`, `uji_serangan.py`, and the interactive Playwright check).
2. **Optional (`R-1` to `R-3`)**: three low-priority design notes are left as they are within the current scope and do not block release readiness.
3. **Local action before manual packaging**: review `git status`/`git diff` before committing and do not include `"API KEY .txt"` or untracked non-repository files if a submission archive is made outside `git`.
