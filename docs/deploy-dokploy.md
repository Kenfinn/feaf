# Deploying FEAF to Dokploy

This repo already has a `Dockerfile`. Dokploy only needs to build it from GitHub. The first
time takes about 15 minutes.

The image has been tested (8 Nov): build, health check, access code, automatic puller,
and data that persists after the container is recreated.

> Environment variables still start with `SENTINEL_` (an internal code name), even though the product is called FEAF.
>
> The menu names below follow a common Dokploy version. If yours differs slightly,
> look for the equivalent. The content is the same: Git source, Dockerfile build type, environment,
> volume, and domain.

---

## 0. Before you start

- Dokploy is already running on your server, and you can log in to its dashboard.
- Dokploy has access to the repo `<owner>/FEAF`. The repo is private, so:
  **Settings → Git → GitHub**, connect the GitHub App, then grant it access to that repo.
- Prepare one random **access code** for the edit buttons, for example the output of this command:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(12))"
```

- First check that your server can reach the exchange OpenAPI. Run this in the server terminal:

```bash
curl -s https://openapi.twse.com.tw/v1/opendata/t187ap04_L | head -c 200
```

  It must return JSON text starting with `[ {"出表日期"`. If you get the page
  "FOR SECURITY REASONS" instead, the server is blocked, and fetching has to be done from a laptop in
  Taiwan.

## 1. Create the application

1. **Projects → Create Project**, name it `feaf`.
2. Inside the project: **Create Service → Application**, name it `feaf-web`.

## 2. Code source

**General** tab, **Provider** section:

| Field | Value |
|---|---|
| Provider | GitHub |
| Repository | `<owner>/FEAF` |
| Branch | `main` |
| Build Path | `/` |

**Build Type** section: choose **Dockerfile**, with Docker File `Dockerfile`.
Do not choose Nixpacks.

## 3. Environment

**Environment** tab, paste and adjust:

```
SENTINEL_KODE_AKSES=fill-in-the-random-code-from-earlier
SENTINEL_SERTAKAN_CONTOH=1
SENTINEL_TARIK_OTOMATIS_DETIK=600
```

| Variable | Purpose |
|---|---|
| `SENTINEL_KODE_AKSES` | Without this code, visitors can only view. The add/delete watchlist buttons and *Check now* only work after opening `/akses?kode=...` once |
| `SENTINEL_KUNCI_BACA` | `1` = lock all read pages (including feed, stocks, valuation, docs). Only active when `SENTINEL_KODE_AKSES` is set. Visitors without the code see a 401 page. Link to share with the judges: `https://<domain>/akses?kode=<code>` |
| `SENTINEL_SERTAKAN_CONTOH` | `1` = the four sample cases (published, injection, USD, skipped) are still shown next to the real data, labelled "sample" |
| `SENTINEL_TARIK_OTOMATIS_DETIK` | Check announcements every N seconds (minimum 300). `600` = every 10 minutes, 24 hours a day, so history builds up on its own |
| `FINMIND_TOKEN` | **Optional, recommended.** Free token from finmindtrade.com for the Financials tab on the stock page. Without a token, the quota is 300 requests per hour (enough for about 100 stocks because results are cached for 12 hours) |
| `GEMINI_API_KEY` | **Optional.** Without it, the agent uses the rule-based reasoner. Set it here, **never** in code |

## 4. Volume (required)

**Advanced → Volumes / Mounts → Add Volume** tab:

| Field | Value |
|---|---|
| Mount Type | Volume |
| Volume Name | `feaf-data` |
| Mount Path | `/data` |

Without this, the watchlist and all announcement history are **lost on every redeploy**.

## 5. Domain

**Domains → Add Domain** tab:

| Field | Value |
|---|---|
| Host | your own subdomain, e.g. `feaf.domainmu.com` (or the generate-domain button from Dokploy) |
| Container Port | `8000` |
| HTTPS | enabled, Let's Encrypt |

If you use your own subdomain, first create a DNS `A` record pointing to the server IP.

## 6. Deploy

Press **Deploy**, then open the **Deployments/Logs** tab. The first build takes about 1–2 minutes.
The success sign in the log:

```
Uvicorn running on http://0.0.0.0:8000
```

Then open in a browser:

| Address | Should show |
|---|---|
| `https://feaf.domainmu.com/sehat` | `{"ok":true, ...}` |
| `https://feaf.domainmu.com/` | The Alerts page, with the language menu EN / 中文 / ID |
| `https://feaf.domainmu.com/akses?kode=<yourcode>` | The message "Access granted", after which the buttons can be used |

A few minutes after startup, the **Last fetch** box in the side menu shows the time of the
first automatic fetch.

## 7. Later updates

Whenever there is a new commit on that branch, press **Deploy** again. You can also enable
**Auto Deploy** in the General tab. Data on the volume stays safe.

---

## What to share with testers

Send two links:

1. **View only:** `https://feaf.domainmu.com/?lang=en` (or `lang=zh` / `lang=id`)
2. **To try the buttons:** `https://feaf.domainmu.com/akses?kode=<yourcode>`.
   Share only with the team. Anyone who has this link can change the watchlist.

### Test checklist for testers

| # | Try | Expected |
|---|---|---|
| 1 | Switch language EN → 中文 → ID | All text changes, including the agent's reasons and check results |
| 2 | Open sample case **2330 · 2026-09-18** | Published, 8/8 checks passed, impact on valuation |
| 3 | Open sample case **2330 · 2026-09-22** (injection) | A "text resembling instructions" warning, but the published figures are still correct |
| 4 | Open sample case **2330 · 2026-09-19** (USD) | Rejected, because a foreign currency is not silently converted |
| 5 | Open the **Audit trail** of one case | Every step is recorded: duration, model calls, tokens, reasons |
| 6 | Watchlist: add a wrong code, e.g. `12;ab` | Rejected with a message |
| 7 | Watchlist: add a stock that is actively announcing, then **Check now** | That day's real announcements appear in Alerts |
| 8 | Open **Valuation 2330** | Reverse DCF, WACC, sensitivity |
| 9 | Type `2330` in the side menu search box | The stock page: price, tabs Stream / Key Stats / Financials / Valuation / Profile |
| 10 | **Financials** tab → Annual → YoY growth | A colored growth table (red = up, green = down) |
| 11 | Stock page → **Summary** tab, switch risk profile from conservative → aggressive | Strengths, points to watch, conclusion, and questions to check. **No** buy/sell wording |

### What is genuinely not there yet (do not report as bugs)

- **The AI model is not active** if `GEMINI_API_KEY` has not been set. The screen says so
  plainly ("rule-based reasoner").
- **Most real announcements end up "skipped".** The list of articles considered
  to affect valuation is still provisional and awaits verification by the finance team
  (`app/agent/screen.py`).
- **Valuation exists only for 2330.** Other issuers are marked "figures only".
- **History starts only from the deploy day.** The exchange OpenAPI contains only the
  current day's announcements. Older history has to be pulled from a laptop on a Taiwan network.
- **The human review queue** has not been built.

---

## 8. Before the demo: Cache Warm-up (Required)

So the demo runs smoothly and the valuation pages of large issuers appear in under 2 seconds with no network delay, run the cache warm-up on the night before the demo.

1. Log in to the server terminal and find the container ID:
   ```bash
   docker ps | grep feaf
   ```

2. Run the cache warm-up script inside the container with the persistent data folder:
   ```bash
   docker exec -it <container_id> python3 scripts/panaskan_cache.py --top 30 --data-dir /data
   ```

   Or for specific issuers that will be opened during the presentation:
   ```bash
   docker exec -it <container_id> python3 scripts/panaskan_cache.py --kode 2330 2317 2454 2308 2382 --data-dir /data
   ```

3. **Estimated time and schedule:**
   - Run it on the night before the demo.
   - Warming up 30 issuers takes about 15–20 minutes when the 25-month price history is fetched for the first time (respecting a polite 2-second pause per official request).
   - If the price history is already in the cache, the process takes under 1 minute.
   - The whole cache is stored on the `/data` volume, so it stays safe and is used by the web app right away.
