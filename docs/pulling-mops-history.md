# Pulling MOPS announcement history → the FEAF server

**Why it is needed:** the server can only fetch **the current day's** announcements (the exchange OpenAPI).
Earlier history, which the gold set and the demo need, exists only on MOPS, and
MOPS **can only be accessed from a Taiwan network**. So: a laptop in Taiwan pulls the data,
then sends the result to the server.

```
Laptop (campus wifi / phone hotspot with a Taiwan SIM)    Server (feaf.example.com)
  spike_mops.py   → list of announcements
  parse_mops.py   → address of each announcement
  fetch_details.py→ full content (personal data removed)
  kirim_riwayat.py ─────────── HTTPS + access code ───►  /api/impor → merged without duplicates
```

No `pip install` needed: the pulling scripts use only the Python 3.9+ standard library.

---

## 0. Preparation (2 minutes)

- Laptop on **campus wifi or a phone hotspot with a Taiwan SIM**. **VPN off.**
- Latest repo:

```bash
git checkout main && git pull
```

## 1. Pull the announcement list (±1 minute)

Use the codes that are in the server watchlist:

```bash
python3 scripts/spike_mops.py --codes 2330 2454 2317 2881 1301
```

✅ Each issuer: `OK — N baris via mopsov.twse.com.tw` (N rows via mopsov.twse.com.tw)
❌ `diblokir` (blocked): the network is not in Taiwan, or the VPN is still on.
❌ `tidak menemukan tabel` (table not found): the MOPS layout changed. Send the `data/raw/*.html` file named in that message to the technical team.

## 2. Get the address of each announcement (seconds)

```bash
python3 scripts/parse_mops.py --since 2026-06-01
```

Start from June first to keep it fast. It can be repeated with an earlier date later.

## 3. Pull the full content (±2.5 seconds per announcement)

```bash
python3 scripts/fetch_details.py --since 2026-06-01 --all
```

Five issuers since June ≈ 400 announcements ≈ **15–20 minutes**. Let it run; the pause is
deliberately slow because MOPS is a public server. **Do not reduce it.**

The result is **merged** into `data/parsed/details.json`, not overwritten. If it is interrupted
midway, run it again; what already exists is skipped.

## 4. Send to the server (±1 minute)

```bash
python3 scripts/kirim_riwayat.py --server https://feaf.example.com
```

The script asks for the **access code** (the value of `SENTINEL_KODE_AKSES` in Dokploy). The code is not
shown as you type it.

✅ `Selesai: N pengumuman baru masuk ke server` (Done: N new announcements entered the server)
❌ `HTTP 403`: wrong access code, or `SENTINEL_KODE_AKSES` has not been set in Dokploy.

Sending twice is safe: what already exists on the server is skipped.

## 5. Check on the web

Open `https://feaf.example.com/?lang=en`. The history appears in **Alerts** and in the **Stream**
tab of every stock page. For announcements that pass the article filter, the agent
calls Gemini **once per announcement**. The result is stored, so later periodic checks
do not call the model again.

---

## Notes

- **Personal data** (`發言人` (spokesperson), job title, phone) is removed on the laptop by `fetch_details.py`,
  and **removed once more** on the server at import.
- **The `data/` folder is not committed.** Do not send `details.json` through chat or git;
  use `kirim_riwayat.py`.
- To add other issuers later: repeat steps 1–4 with the new `--codes`.
  Old announcements that were already sent are not duplicated.
