# FEAF flow diagrams

Three specification diagrams and the multi-turn chat flow, drawn from the `v1.1.0` code as of 13 Nov 2026 (full technical details are in [`docs/system-design.md`](system-design.md)).
When the code changes, these diagrams change with it: they are a specification, not an illustration. The static images of the first version are in `docs/diagram/` and must be re-rendered separately if used outside Markdown.

1. [System flow](#1-system-flow): where data comes from, which components it passes through, where it is shown
2. [Agent flowchart](#2-agent-flowchart-one-announcement): the fate of one announcement through both the valuation path and the deterministic signal path, plus the Ask FEAF flow
3. [App check flowchart](#3-app-check-flowchart): the order of checks that the app on the server is really running

---

## 1. System flow

```mermaid
flowchart LR
  classDef luar fill:#EEF2F6,stroke:#8A9BB0,color:#1B2A3A
  classDef model fill:#E3F4EE,stroke:#2E8B6A,color:#0F3D2E
  classDef inti fill:#FFF6E0,stroke:#C98A0B,color:#4A3305
  classDef simpan fill:#F3EEFA,stroke:#7A5BB5,color:#2E1E4D
  classDef layar fill:#1B3A5C,stroke:#1B3A5C,color:#FFFFFF

  subgraph SUMBER["Data sources"]
    OA["TWSE / TPEx OpenAPI<br/>daily 重大訊息 announcements<br/><i>reachable from anywhere</i>"]:::luar
    PX["TWSE / TPEx Official & OpenAPI<br/>daily prices · TAIEX · PER/PBR · profile"]:::luar
    FM["FinMind<br/>income statement · balance sheet · cash flow"]:::luar
    MOPS["MOPS<br/>announcement history<br/><i>Taiwan network only</i>"]:::luar
  end

  subgraph LAPTOP["Relay on a Taiwan network"]
    SK["spike_mops -> parse_mops<br/>-> fetch_details"]:::inti
    KR["kirim_riwayat.py"]:::inti
  end

  subgraph SERVER["FEAF server · FastAPI (uvicorn --workers 1)"]
    PM["Automatic monitor<br/>TARIK_OTOMATIS_DETIK (floor 300 s)"]:::inti
    CN["Check now button"]:::inti
    TK["Puller (tarik.py)<br/>check BLOCK_MARKERS · drop PII_LABELS · deduplicate"]:::inti
    IM["/api/impor<br/>requires KODE_AKSES · max 5000"]:::inti
    DB[("/data (SENTINEL_DATA_DIR)<br/>parsed · watchlist · traces<br/>traces_chat · cache_model")]:::simpan
    MN[("valuation/inputs/*.json<br/>data/fixtures/")]:::simpan
    AG["Agent (6 clause paths)<br/>screen -> extract/signal -> triage<br/>-> verify -> recompute -> verify"]:::inti
    UB["Per-article thresholds<br/>umpan_balik.py · history max 500"]:::simpan
    RV["Human review decisions<br/>keputusan_review.json"]:::simpan
    VO["Automatic valuation & Summary<br/>FinMind + harga_resmi + background beta + profile"]:::inti
    PS["Market data & TTL cache<br/>pasar.py · harga_resmi.py · indeks_nama.py"]:::inti
    CH["Ask FEAF (chat.py)<br/>TOLAK · HMAC history · 13 TOOLS · periksa_jawaban"]:::inti
  end

  GM["Gemini (MODEL + MODEL_CADANGAN)<br/>clause 20 extraction · optional narration · Ask FEAF<br/>never computes numbers"]:::model

  subgraph LAYAR["Web · EN / 中文 / ID"]
    W1["Watchlist"]:::layar
    W2["Alerts + detail"]:::layar
    W3["Audit trail"]:::layar
    W4["Stock page<br/>Summary · Stream · Key Stats<br/>Financials · Valuation · Profile"]:::layar
    W5["Review · Thresholds"]:::layar
    W6["Ask FEAF"]:::layar
  end

  MOPS --> SK --> KR -->|HTTPS| IM --> DB
  PM --> TK
  CN --> TK
  OA --> TK --> DB
  DB --> AG
  AG <-->|"clause 20 / rule fallback"| GM
  AG -->|"result + trace"| DB
  AG -->|"clause 31 triggers refresh"| VO
  UB --> AG
  RV --> AG
  W5 -->|"👍/👎, approve/archive"| UB
  W5 --> RV
  PX --> PS
  FM --> PS
  PS --> VO --> AG
  MN --> VO
  PS --> W4
  VO --> W4
  CH <-->|"tool calling <= 5 steps"| GM
  PS --> CH
  VO --> CH
  DB --> CH
  CH --> W6
  DB --> W1
  DB --> W2
  DB --> W3
  DB --> W4
```

| Box / Subsystem | Main files |
|---|---|
| Configuration & version | `app/config.py`, `app/versi.py` |
| Puller, watchlist, import, read-store | `app/tarik.py`, `app/store.py`, `scripts/tarik.py` |
| Automatic monitor, read middleware, web & API routes | `app/main.py` |
| Valuation agent & 6 signal paths | `app/agent/pipeline.py`, `screen.py`, `extract.py`, `sinyal.py`, `triase.py`, `verify.py`, `recompute.py` |
| 👍/👎 thresholds, human review, risk profile | `app/umpan_balik.py`, `app/review.py`, `app/ambang_profil.py` |
| Automatic valuation, official prices, summary, citations | `app/valuasi_otomatis.py`, `app/harga_resmi.py`, `app/ringkasan.py`, `app/sitasi.py`, `scripts/dcf.py` |
| Market data & issuer search index | `app/pasar.py`, `app/indeks_nama.py` |
| Ask FEAF (server & browser UI) | `app/chat.py`, `app/static/chat.js`, `app/templates/_panel_chat.html` |
| Gemini + SHA-256 cache + circuit breaker | `app/agent/llm.py` |
| History from a laptop on a Taiwan network | `scripts/spike_mops.py`, `parse_mops.py`, `fetch_details.py`, `kirim_riwayat.py` |

**Data source note:** The TWSE/TPEx daily announcement OpenAPI can be fetched from anywhere with periodic update intervals, while the older MOPS history can only be pulled from a Taiwan network and then sent to `/api/impor`.

---

## 2. Agent flowchart (one announcement)

```mermaid
flowchart TD
  classDef akhir_ok fill:#1B3A5C,stroke:#1B3A5C,color:#FFFFFF
  classDef akhir_tahan fill:#FBF2E3,stroke:#C98A0B,color:#5F4409
  classDef akhir_lewat fill:#E3E6EA,stroke:#8A939E,color:#3A434D
  classDef akhir_tolak fill:#F9EAE8,stroke:#B3392B,color:#6B2620
  classDef model fill:#E3F4EE,stroke:#2E8B6A,color:#0F3D2E
  classDef kode fill:#FFFFFF,stroke:#8A9BB0,color:#1B2A3A
  classDef manusia fill:#F3EEFA,stroke:#7A5BB5,color:#2E1E4D

  A(["FETCHED · VALIDATED<br/>PII_LABELS dropped · deduplicated"]):::kode --> B{"SCREENED (screen.py)<br/>KLAUSA_RELEVAN + LABEL_CAPEX + _ANTAR_GRUP"}:::kode
  B -->|"Clause 20 inter-group 100%"| X1(["ARCHIVED<br/>filtered before the LLM"]):::akhir_lewat
  B -->|"Clause 22/23 · 11/35 · 31 · 7/8 · 1/3/40"| S1["EXTRACTED · signal (sinyal.py)<br/>deterministic parser, no Gemini"]:::kode
  S1 --> S2["VERIFIED · source<br/>sinyal.periksa_kutipan()"]:::kode
  S2 --> S3{"Policy gating<br/>ambang_profil.py<br/>moderate hold / conservative archive"}:::kode
  S3 -->|publish| P_SIG(["PUBLISHED<br/>verified signal card"]):::akhir_ok
  S3 -->|archive| X_SIG(["ARCHIVED<br/>below the materiality threshold"]):::akhir_lewat
  S3 -->|hold| H_SIG(["HELD · sinyal / sinyal_rusak"]):::akhir_tahan

  B -->|"Clause 20, LABEL_CAPEX, or doubtful article"| C{"llm.jalan(): Gemini key present,<br/>run quota & breaker healthy?"}:::kode
  C -->|no| R["Rule-based reasoner (_sari_aturan)<br/>LABEL_SAH · SATUAN · MATA_UANG"]:::kode
  C -->|yes| D["TRIAGED · EXTRACTED<br/>Gemini inside the &lt;dokumen&gt; fence (or SHA-256 cache)<br/>PENANDA_INJEKSI records telemetry"]:::model
  D -->|failed / fallback| R
  D --> H
  R --> H{"Is there a number<br/>with its source sentence?"}:::kode
  H -->|no| X2(["HELD · tanpa_angka (no figures)<br/>cannot be approved manually"]):::akhir_tahan
  H -->|yes| T{"TRIAGED · confidence<br/>BASE 0.55 (0.45 without article)<br/>+ 0.10 proven number + PITA_MATERIAL"}:::kode
  T -->|"score < threshold - 0.05"| X3(["ARCHIVED<br/>score below the doubt zone"]):::akhir_lewat
  T -->|"doubt zone [threshold - 0.05, threshold)"| X4(["HELD · low confidence"]):::akhir_tahan
  T -->|"score >= threshold"| I{"Is there a valuation model?<br/>manual or automatic"}:::kode
  I -->|no| X5(["HELD · no valuation"]):::akhir_tahan
  I -->|yes| J{"VERIFIED · source (7 checks)<br/>label · quote · number · mu<br/>unit · conversion · magnitude"}:::kode
  J -->|all pass| L["VALUED<br/>recompute.py -> dcf.compute() before vs after"]:::kode
  L --> M{"VERIFIED · arithmetic<br/>drift <= 1e-6%?"}:::kode
  M -->|yes| X7(["PUBLISHED<br/>alert + source + DCF delta"]):::akhir_ok
  M -->|no| X_REJ(["REJECTED<br/>circularity check failed"]):::akhir_tolak
  J -->|fail| X6(["HELD · verification<br/>doubtful (CEK_RAGU) -> may be approved<br/>non-doubtful -> archive only"]):::akhir_tahan

  H_SIG & X2 & X4 & X5 & X6 --> HR["HUMAN REVIEW (_terapkan_review)<br/>approved confidence -> must still pass Stage 4"]:::manusia
  HR -->|approve valid| P2(["PUBLISHED<br/>approved by a human, recorded"]):::akhir_ok
  HR -->|archive| A2(["ARCHIVED<br/>archived by a human, recorded"]):::akhir_lewat
  X7 --> UB["👍/👎 investor (umpan_balik.py)<br/>clamp(0.55 + 0.05*👎 - 0.02*👍, 0.40, 0.90)"]:::manusia
```

In the announcement pipeline, LLM calls are limited to extraction on the valuation path (Clause 20, the `LABEL_CAPEX` override, or an unreadable article) with a deterministic rule fallback. The signal paths (`22/23`, `11/35`, `31`, `7/8`, `1/3/40`) work entirely deterministically in `app/agent/sinyal.py`. All final decisions are recorded in `DATA_DIR/traces/<id>.json`.

### Ask FEAF flow (multi-turn, 13 tools)

```mermaid
flowchart LR
  Q["/api/tanya or POST /tanya<br/>question + sessionStorage history (max 12)"] --> LIM["Rate limit _jam<br/>60 requests/hour"]
  LIM --> REJ{"TOLAK guard<br/>prediction / order / injection / PII?"}
  REJ -->|hit| T_REJ["Deterministic refusal answer + tanda()"]
  REJ -->|pass| HIS["_bersihkan_riwayat()<br/>verify HMAC tanda() (<= 6 of 50 turns)<br/>+ resolve _kode_aktif() & _kalimat_konteks()"]
  HIS --> LOOP{"Recap / Gemini (<= 5 steps)<br/>/ fallback _rencana_aturan"}
  LOOP <--> ALAT["13 read-only tools (ALAT)<br/>7 stock: price · statistics · reports · announcements · valuation · summary · search<br/>6 menu: feed · alerts · trace · review · thresholds · watchlist"]
  LOOP --> VER{"periksa_jawaban()<br/>numbers present in tools/question/HMAC history?<br/>free of TERLARANG words?"}
  VER -->|pass| OUT["HMAC tag 32-hex + traces_chat/<id>.json<br/>rendered via textContent"]
  VER -->|fail| FB["_ringkas_template() from tool results<br/>+ HMAC tag + traces_chat/"]
```

---

## 3. App check flowchart

The order of checks after a deploy, or when something behaves strangely. Follow from the top.

```mermaid
flowchart TD
  classDef ok fill:#E3F4EE,stroke:#2E8B6A,color:#0F3D2E
  classDef salah fill:#F9EAE8,stroke:#B3392B,color:#6B2620
  classDef cek fill:#FFFFFF,stroke:#1B3A5C,color:#1B2A3A

  S(["Start"]):::cek --> A{"Open /sehat<br/>shows ok: true & VERSI_KODE?"}:::cek
  A -->|no| A1["Container / server log<br/>find the last error line<br/>check port 8000 and --workers 1"]:::salah
  A -->|yes| B{"Side menu · Reasoning engine<br/>shows the active model name (not rule-based)?"}:::cek
  B -->|no, rule-based reasoner| B1["Check the API key / model env<br/>then restart the container"]:::salah
  B -->|yes| C{"Side menu · Last fetch<br/>green dot and updated?"}:::cek
  C -->|red| C1["Watchlist -> see the fetch status box<br/>hit BLOCK_MARKERS? -> check the network"]:::salah
  C -->|never| C2["Check SENTINEL_TARIK_OTOMATIS_DETIK<br/>(floor 300 s) or press Check now"]:::salah
  C -->|green| D{"/akses then Watchlist<br/>adding an issuer succeeds?"}:::cek
  D -->|locked| D1["Check KODE_AKSES / KUNCI_BACA<br/>and the HMAC access cookie"]:::salah
  D -->|yes| E{"Alerts · open a sample case<br/>status PUBLISHED & 7/7 checks passed?"}:::cek
  E -->|not shown| E1["Check SERTAKAN_CONTOH=1<br/>or that data/fixtures/ is present"]:::salah
  E -->|yes| F{"Audit trail /jejak/{id}<br/>Model calls >= 1 or cache >= 1?"}:::cek
  F -->|0 and fallback mode: yes| F1["Check HTTP status 400/401/402/403/404<br/>or the breaker in the trace & cache_model/"]:::salah
  F -->|yes| G{"Open stock page 2330<br/>Financials tab & daily prices appear?"}:::cek
  G -->|FinMind / official price message| G1["Check the FinMind quota or the 2 s pause<br/>harga_resmi.py (HTTP 307/429)"]:::salah
  G -->|yes| V{"Valuation tab of a non-financial issuer<br/>shows an automatic DCF?"}:::cek
  V -->|no| V1["Check industry status (17 = tidak_berlaku, not applicable)<br/>or FCFF <= 0 / 12-hour TTL"]:::salah
  V -->|yes| Q{"/tanya or /api/tanya<br/>test a question + multi-turn follow-up?"}:::cek
  Q -->|failed / wrong fallback| Q1["See /api/tanya/jejak/&lt;id&gt;<br/>and the files in traces_chat/"]:::salah
  Q -->|yes| H{"Switch language EN / 中文 / ID<br/>do all labels change?"}:::cek
  H -->|yes| Z(["App fully running"]):::ok
  H -->|no| H1["Check templates & the dictionary app/teks/"]:::salah
```
