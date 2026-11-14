# Data Access Techniques: MOPS / TWSE / TPEx

Technical notes for the 72-hour test (Phase 0). Run `python3 scripts/probe_sources.py`
from the campus network to confirm which sources are reachable.

---

## Key finding before you start

**TWSE, TPEx, and MOPS block IPs from outside Taiwan and datacenter IPs, with HTTP 200.**

The block page contains the text "FOR SECURITY REASONS, THIS PAGE CAN NOT BE ACCESSED"
but the status code is still 200. A pipeline that only checks `response.status_code == 200`
will record it as a success and store junk HTML in the database.

Two consequences:

1. **Run from the campus network in Taiwan.** If you later deploy to the cloud (AWS/GCP),
   this will fail again, so plan for it from the start.
2. **Validate the response shape, not the status code.** Every fetcher must check that
   the result really is the expected JSON/table. This is also good material for the
   *failure handling* page in the deck (page 7 of Appendix 1).

---

## Three layers of sources

### Layer 1: Official OpenAPI (cleanest, use this first)

| Source | Base URL | Format |
|---|---|---|
| TWSE | `https://openapi.twse.com.tw/v1` | REST JSON, no authentication |
| TPEx | `https://www.tpex.org.tw/openapi/v1` | REST JSON, no authentication |

The full endpoint list is at each one's `/swagger.json`. Coverage: daily prices,
valuation (PER/PBR/yield), institutional trading, monthly revenue, indices, and
some financial statement data.

Field notes:
- Older endpoints use the **ROC calendar (民國)**: year 2026 = year 115. It must be converted.
- Pause between requests (0.5–1 second). There is no official rate limit documentation, so be polite.
- Some endpoints return CSV even when JSON is requested. Check the `Content-Type`.

### Confirmed from the 14 September 2026 fetch

Run from the campus network in Taiwan, 5 issuers, 711 announcements, 100% cited:

| Fact | Value |
|---|---|
| Serving host | `mopsov.twse.com.tw` — **not** `mops.twse.com.tw`, which refuses even from Taiwan |
| List endpoint | `POST /mops/web/ajax_t05st01` with `co_id`, `year` (ROC), `step=1`, `firstin=1` |
| Table columns | 公司代號 (company code) · 公司名稱 (company name) · 發言日期 (announcement date) · 發言時間 (announcement time) · 主旨 (subject) · [詳細資料 (details) button] |
| Market type parameter | `TYPEK=sii` for listed companies — not `all` |
| Address per announcement | `GET /mops/web/ajax_t05st01?step=2&firstin=1&TYPEK=sii&co_id=…&seq_no=…&spoke_date=…&spoke_time=…` |
| Coverage | One full ROC year per request (115 = 1 Jan – 11 Sep 2026) |

The address parameters live inside the `onclick` of the 詳細資料 button, in the form
`fieldName.value='value';` — not in the cell text. Without reading them, an announcement
has no address the judges can verify.

### Layer 2: MOPS (the actual disclosure source, has no REST API)

MOPS is a form-POST that returns an HTML table, not an API. It is the main source for
**重大訊息 (material event announcements)** — the core of the watchlist-monitoring agent.

Domains (all three serve the same content, useful as fallbacks):
- `mops.twse.com.tw` — primary
- `mopsov.twse.com.tw` — backup
- `mopsc.twse.com.tw` — new version

Relevant endpoints:

| Path | Content |
|---|---|
| `/mops/web/ajax_t51sb10` | 重大訊息 — material event announcements |
| `/mops/web/ajax_t163sb04` | 綜合損益彙總表 — comprehensive income summary |
| `/mops/web/ezsearch` | 公告快易查 — quick announcement search |

Technique: POST `application/x-www-form-urlencoded` with parameters such as
`step`, `firstin`, `TYPEK` (`sii` = listed, `otc` = OTC), `year` (ROC year), `season`.
Then parse the table with `pandas.read_html()` or BeautifulSoup.

Common pitfalls:
- The table structure changes between report types — do not assume fixed column indexes.
- Mixed Big5/UTF-8 encoding in older data.
- Aggressive rate limiting. Pause 1–3 seconds and prepare a retry with backoff.
- Investor conference materials are **PDFs** and need separate extraction.

### Layer 3: Aggregators (for speed, not a substitute for citations)

[FinMind](https://finmind.github.io/) — free, sourced from MOPS, no token needed
(300 requests/hour; 600 with a free token). Verified reachable even from outside Taiwan.

```python
from FinMind.data import DataLoader
api = DataLoader()
api.taiwan_stock_financial_statement(stock_id="2330", start_date="2026-01-01")
```

**Two binding rule notes:**

1. An aggregator is a **third-party resource** → it must be disclosed in the declaration form and
   its license complied with (Article 13.4).
2. The challenge description asks that the main basis be public information that can be **traced**.
   So an aggregator may be used for speed, but **the citation shown to the user
   must point to the original MOPS/TWSE URL**, not to the aggregator endpoint.

The safe strategy: the aggregator as the fast path and fallback, MOPS as the citation source.

---

## Specific techniques for the monitoring agent

1. **Detect changes via snapshot + diff.** Fetch the 重大訊息 list periodically, hash each
   entry, and compare with the previous snapshot. What is new is the agent trigger. Far
   cheaper than reprocessing everything.
2. **Store the source URL + fetch timestamp in every document.** This is what makes
   *traceable* provable, and without it citations cannot be verified by the judges.
3. **Separate numbers into structured storage.** The foundation of the verifier: every number in the output
   is matched against this storage. No match → reject and escalate to a human.
4. **Cache aggressively.** It lowers API cost — and cost is one of the mandatory Appendix 2
   metrics that must be reported in the final.
5. **Record every fetch failure as an event.** It also becomes material for the *operation trace*
   that must be included in the final, so do not throw it into `/dev/null`.

---

## Sources

- [TWSE OpenAPI](https://openapi.twse.com.tw/)
- [TPEx OpenAPI](https://www.tpex.org.tw/openapi/)
- [公開資訊觀測站 MOPS](https://mops.twse.com.tw/mops/web/index)
- [FinMind](https://github.com/FinMind/FinMind)
- [政府資料開放平臺](https://data.gov.tw/)
