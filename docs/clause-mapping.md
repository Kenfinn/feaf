# Draft mapping of 重大訊息 clauses (material-information announcements) to agent actions

**Status: DRAFT, awaiting verification by the finance team.** Prepared by the technical team, 10 Nov 2026.
Once approved, the content moves to `app/agent/screen.py` (`KLAUSA_RELEVAN`) and the item
labels to `app/agent/extract.py` (`LABEL_SAH`).

## Why a change is needed

The current list (11, 20, 22, 2) was guessed before any real data existed. The real data from
9 Nov (578 TWSE + TPEx announcements) shows:

1. **Clause 31 (quarterly financial report) accounts for 177 (31%) and has been SKIPPED so far**,
   although it is the most relevant clause for valuation.
2. **Clause 11 is not capital expenditure.** It covers bond issuance/conversion, capital
   reduction, and cancellation of treasury shares: what changes is the **number of shares**.
3. **Clauses 22/23 (guarantees / lending of funds to other parties) are not the company's own
   debt**, so they are not suitable as a replacement for long-term debt in the DCF.
4. **Clause 2 does not appear at all.** Bond defaults appear under **clause 1** instead.
5. **The item labels the checker looks for do not exist in the real announcements** (e.g.
   `交易金額`). The real labels are listed in the last column of the evidence table below.
6. TWSE and TPEx numbering is the same for almost all clauses, **except "miscellaneous"**:
   TWSE clause 51, TPEx clause 53.

Two technical fixes are already done (no verification needed): units such as `(仟元)`
(thousands of NTD) are now read from the label, and sub-items `(1)(2)(3)…` are parsed separately.

## Proposal

Four kinds of action:
- **Valuation**: the figure changes DCF inputs, recalculated
- **Report**: a quarterly report triggers an update of fundamentals and DCF (new path, B2)
- **Risk signal**: does not change the DCF, but is published as a risk alert with its figures;
  serious ones go straight to HELD for a human
- **Skipped**: archived with a reason, never reaches the model

| Clause | Content (from real data) | Now | **Proposal** | Input / action | Item labels used |
|---|---|---|---|---|---|
| **31** | Quarterly financial report approved by the board | skipped | **Report** | Revenue, operating profit, YTD net profit, total assets/liabilities/equity → compare with the prior-year YTD, update the DCF | `1月1日累計至本期止營業收入(仟元)` etc., `期末總資產(仟元)`, `期末總負債(仟元)` |
| **20** | Acquisition/disposal of assets (machinery, buildings, right-of-use assets, investment products) | capex, cash | **Valuation** | capex (fixed assets, right-of-use) or cash (investment products, disposals); the model sorts them | `交易單位數量、每單位價格及交易總金額` (free text, needs the model) |
| **11** | Bond issuance/conversion, capital reduction, treasury shares cancelled | capex ❌ | **Valuation** | **Number of shares** (new input), not capex | `全案發行總金額及股數`, `減資金額`, `發行總額` |
| **35** | Share buyback | skipped | **Valuation** | Cash outflow + number of shares | `本次已買回股份總金額(元)` |
| **10** | Important contracts (e.g. syndicated loan) | skipped | **Valuation** | Debt if it is a loan contract; the model sorts them | (varies, needs the model) |
| **22** | Guarantees (背書保證) | debt ❌ | **Risk signal** | Guarantee balance and its ratio to equity | `迄事實發生日止背書保證餘額(仟元)`, `…占…淨值之比率` |
| **23** | Lending of funds to other parties (資金貸與) | skipped | **Risk signal** | Loan balance and its ratio to equity | `迄事實發生日止資金貸與餘額(仟元)`, `…占…淨值之比率` |
| **1** | Default / matured bond not repaid | skipped | **Risk signal, straight to HELD** | Amount in default | `喪失債信之金額` |
| **3** | Production halt, mass layoffs | skipped | **Risk signal, straight to HELD** | — | — |
| **40** | Trading halt of the shares | skipped | **Risk signal, straight to HELD** | — | — |
| **28** | Problematic customer/debtor | skipped | **Risk signal** | Affected receivables/guarantees | `債權種類或背書保證金額及其所占資產比例` |
| **26** | Cybersecurity incident | skipped | **Risk signal** | — | — |
| **51 (TWSE) / 53 (TPEx)** | Miscellaneous: media clarifications, figure corrections, name changes, etc. | skipped | **Model triage** | The model decides whether it is relevant, with a confidence score | `更正前/後金額`, `近期營業收入及損益資訊` |
| 14 | Dividend | skipped | Skipped | Does not change free cash flow | — |
| 12 | Investor conference | skipped | Skipped | — | — |
| 6, 7, 8 | Changes of directors, auditor, management | skipped | Skipped | (candidate governance signal in a later version) | — |
| 16, 17, 18, 21, 36, 43, 44, 47, 52 | Shareholder meetings, non-compete waivers, donations, independent director objections, etc. | skipped | Skipped | — | — |
| 2 | (does not appear in the data) | debt, cash | **Remove** | The initial guess of "bounced cheques" was not confirmed | — |

## Questions for the finance team

Answer directly in this document or in the team chat. "Agree" or the correction is enough.

1. **Clause 31:** agree to make it the trigger for a fundamentals + DCF update?
2. **Clauses 22/23:** agree to treat them as a **risk signal**, not a DCF input? From what
   threshold should the balance/equity ratio count as needing an alert? (proposal: ≥ 50%, matching
   the limit that actually triggers a reporting obligation in the regulation)
3. **Clauses 11 and 35:** agree that the impact is on the **number of shares** (fair value per share)?
4. **Clauses 1, 3, 40:** agree they are always HELD for a human?
5. **Clauses 51/53:** agree to hand them to model triage, or simply skip them?
6. **Clauses 6/7/8 (governance):** keep skipping them for now?
7. **Regulation text:** please match the title of each clause against the official text of
   《對有價證券上市公司重大訊息之查證暨公開處理程序》 Article 4 (TWSE) and the TPEx version.
   The official document cannot be downloaded from outside Taiwan, so the "Content" column above
   was compiled from the titles of the real announcements.
8. **Clause 20, single-transaction figures** (e.g. machinery of NTD 108 million): at present that
   figure *replaces* the year's capital expenditure in the DCF (suitable for a board capex budget,
   not for a single transaction), so it is almost always held by the magnitude checker.
   Proposal: a single transaction is *added* to the current-year capex. Agree?
9. **Triage materiality** (`app/agent/triase.py`): amount ÷ market capitalization —
   ≥ 2% material, ≥ 0.5% moderate, ≥ 0.05% small, below that trivial (archived). In the
   10 Nov data, 7 of 55 clause 20 announcements fall into "trivial" (office space rentals of a few
   million NTD). Are these limits reasonable in your view?

## Team decisions (finance team answers, 11 Nov)

Source: the finance team's written answers to the clause 11/22 questions (internal team
material, not published) (Q1–Q9) and their follow-up questions. This section is the B1
specification. Where it conflicts with the "Proposal" table above, this section prevails.

### General principle: cash-based DCF

The DCF moves only when cash actually moves. Announcements of plans, board approvals, or
issuance ceilings do not change the DCF; what changes the DCF is the quarterly financial report
(clause 31) that contains the realized figures. **This also applies to clause 20** (capex plans
and acquisitions). As a result: such announcements become signals, and the recalculation that
exists today is shown as an "if realized" scenario, not as a new valuation.

### Clause 22 (guarantees, 背書保證) and 23 (lending of funds, 資金貸與)

| Aspect | Decision |
|---|---|
| Type | Risk signal. Does not change the DCF (Q1). Clause 23 is treated the same way (Q5) |
| Figures displayed | Total balance (item 7), new guarantee (2.(5)), balance-to-equity ratio (item 8), combined ratio of guarantees + investments + loans (item 9), and the **limit-usage ratio = item 7 ÷ item 6** (Q2). Example 2347: 100,663,762 ÷ 185,566,638 = 54%, leaving 46% to the limit |
| Several recipients in one announcement | Shown **per recipient**, not summed (follow-up Q2) |
| Threshold | Item 8 ratio **≥ 80%** or limit-usage ratio **≥ 80%** → the signal is marked serious and held for a human. Below the threshold → published as info (follow-up Q3) |
| Internal vs external parties | Recipients that are **related parties** (subsidiary, parent, affiliate, as in the notes to the financial statements) are distinguished from outside parties; outside parties get a higher risk weight (Q4). In the data this is read from item 與提供背書保證公司之關係 (relationship with the guarantor company) |

### Clause 11 (changes in capital and debt securities) and 35 (buyback)

| Type | Decision |
|---|---|
| Cancellation of treasury shares (庫藏股註銷) | Does not change shares outstanding, because treasury shares have not counted as outstanding since they were bought back. Does not change the DCF (correction Q6-A) |
| Capital reduction to cover losses (彌補虧損減資) | Info or signal **depending on risk profile**: conservative and moderate → signal, aggressive → info (follow-up Q6) |
| Bond issuance, including convertible bonds | Signal. When used to repay debt, net debt does not change; conversion = potential dilution without a figure because the conversion price is announced later (Q6-B, Q7) |
| Issuance ceiling (發行總額上限) | Not used as a DCF figure; wait for realization (Q8) |
| New shares from conversion / employee options (增資基準日, capital increase record date) | Number of shares rises (dilution) (Q6-C) |
| Materiality | Alert when the share change is **≥ 1%** or the money amount is **≥ 2% of market capitalization**; below that it is archived with a reason (Q9) |

### Implementation status (B1, 11 Nov)

Installed in `app/agent/screen.py` (per-clause path), `app/agent/sinyal.py` (parser),
`app/ambang_profil.py` (thresholds per risk profile), `app/agent/pipeline.py` (decision),
`app/templates/_sinyal.html` (display). Thresholds are selected through the risk profile
(conservative / moderate / aggressive); moderate = the finance team's answer, the other two are
technical team proposals awaiting the team's check:

| Threshold | Conservative | Moderate | Aggressive |
|---|---|---|---|
| Guarantee/loan balance ÷ equity | ≥ 50% | ≥ 80% | ≥ 100% |
| Limit usage (item 7 ÷ 6) | ≥ 70% | ≥ 80% | ≥ 90% |
| Share change | ≥ 0.5% | ≥ 1% | ≥ 2% |
| Money amount ÷ market capitalization | ≥ 1% | ≥ 2% | ≥ 5% |
| Capital reduction to cover losses | signal | signal | info |
| Quarterly-report debt ratio (liabilities ÷ assets), 11 Nov calibration | ≥ 40% | ≥ 50% | ≥ 65% |
| Clause 23 fund lending ÷ equity = needs attention, 11 Nov calibration | ≥ 40% | ≥ 40% | ≥ 40% |

11 Nov calibration from the finance team's gold set: see [`gold-set-results.md`](./gold-set-results.md).
Also: new shares whose number cannot be read = needs attention; clause 20 with a 100%-owned
subsidiary = archive.

The review queue (HELD) uses moderate. Archiving as not material uses the loosest threshold
(conservative). Interim choices by the technical team while awaiting the team:
- 現金減資 (cash capital reduction) → "needs attention" signal.
- Clause 23 uses the same serious threshold as clause 22, plus "needs attention" from 40% of equity (the regulatory limit).
- Clauses 1, 3, 40 → always HELD (may be approved after review). The name item in clause 1
  (公司名稱(或負責人姓名)) is not extracted because it may be a person's name.
- Clauses 51/53, 6, 10, 26, 28 → skipped. Clauses 7/8 → governance signal (finance team answer, 11 Nov).
- Clause 31 → summary of figures from the announcement body (revenue, profit, EPS, assets, liabilities,
  YTD equity), then the automatic valuation of watchlist issuers is rebuilt.

Result on the 578 real announcements of 10 Nov (without the model): 177 reports, 38 guarantee/
loan signals, and 26 capital signals published; 6 serious risks and 4 severe events held for a
human; 783 signal pages displayed in three languages without errors.

### Finance team follow-up answers (11 Nov midday) and their implementation

| Clause | Answer | Implementation |
|---|---|---|
| 1, 3, 40 | Agree to always hold | Done (B1) |
| 6 (corporate-entity director) | May be skipped | Still skipped |
| 7 (external auditor) | Auditor changes are rare, should be reported as info | Governance signal. Partner rotation within the same firm = Info. Firm changed = Needs attention. Former auditor resigns or disagrees on opinion = Serious, held for review |
| 8 (officers) | Important, should be reported | Governance signal. A key position (finance, accounting, internal audit, CEO/managing director/president/COO, board chair) leaving (辭職/資遣/解任/死亡: resignation/layoff/dismissal/death) = Needs attention. Other key positions = Info (conservative: Needs attention). Other positions = Info |

Names of accountants and officers are not extracted: items labeled 姓名 (name) are not quoted and
the free text 異動原因 (reason for change) is not used. The levels above are proposals from the technical team, to be checked by the finance team.

### Still open

- Cash capital reduction (現金減資): shares fall and cash goes out to shareholders at the same time. Not yet asked about specifically.
- Clause 23: to the technical team's knowledge the regulation limits total fund lending to about 40% of equity (far below guarantees). Needs checking against the official text before the 80% threshold is used for clause 23.
- Clauses 51/53 not yet answered (currently skipped).
- Questions 1, 4–9 in the "Questions for the finance team" section above (clause 31, 1/3/40, 51/53, 6/7/8, regulation text, clause 20 transaction semantics, triage materiality limit). Question 8 is partly answered by the cash-based principle.

## Evidence: statistics of the real announcements of 9 Nov

Produced by `scripts/statistik_pasal.py`. On the server, the same script reads the whole
archive since 8 Nov:

```bash
python3 scripts/statistik_pasal.py --contoh 3
```

From 578 unique announcements (2026-11-09 to 2026-11-09), 2 archive files.

| Clause | TWSE | TPEx | Current filter | Example titles | Item labels containing amounts |
|---|---|---|---|---|---|
| 31 | 108 | 69 | skipped | 公告本公司董事會通過115年度第三季合併財務報告 · 公告本公司115年第3季合併財務報告業經提報董事會 | 1月1日累計至本期止稅前淨利 (仟元) · 1月1日累計至本期止本期淨利 (仟元) · 1月1日累計至本期止歸屬於母公司業主淨利 (仟元) · 期末總資產 (仟元) |
| 20 | 42 | 13 | passed → capex, cash | 代孫公司濟南聯合製罐有限公司公告取得理財商品 · 本公司向關係人取得使用權資產 | 交易相對人為關係人者，並應公告選定關係人為交易對象之 · 交易標的最近五年內所有權人曾為公司之關係人者，尚應公 · 估價報告是否為限定價格、特定價格或特殊價格 · 交易單位數量、每單位價格及交易總金額 |
| 12 | 31 | 20 | skipped | 本公司受邀參加凱基證券舉辦之線上法人說明會 · 本公司受邀參加福邦證券舉辦線上法人說明會。 | — |
| 51 | 50 | 0 | skipped | 公告本公司名稱由「世紀離岸風電設備股份有限公司」更名 為「世 · 澄清媒體報導 | 近期營業收入及損益資訊 · 歷史每月營業收入 · 更正前金額/內容/頁次 · 更正後金額/內容/頁次 |
| 53 | 0 | 31 | skipped | 公告本公司名稱由「森寶開發股份有限公司」更名為 「長耀地產投 · 本公司骨質疏鬆症生物相似藥SPD8（Denosumab） 正 | 更正前金額/內容/頁次 · 更正後金額/內容/頁次 · 115/11/09期初餘額$1,966,696。 預 · 規劃貸與金額回收 |
| 8 | 19 | 10 | skipped | 公告本公司會計主管異動 · 代重要子公司騰輝電子(蘇州)有限公司公告總經理異動 | — |
| 6 | 20 | 9 | skipped | 公告本公司法人董事代表人逝世 · 代子公司信益陶瓷(中國)有限公司公告法人董事代表人逝世 | — |
| 11 | 19 | 10 | passed → capex | 公告本公司董事會決議庫藏股註銷減資基準日 · 公告本公司國內第二次有擔保及第三次無擔保轉換 公司債115年 | 發行價格 · 全案發行總金額及股數 · 採總括申報發行新股案件，本次發行金額及股數 · 採總括申報發行新股案件，本次發行後，剩餘之金額及股數 |
| 23 | 15 | 10 | skipped | 依公開發行公司資金貸與及背書保證處理準則第二十二條第一項 第 · 本公司對昶和纖維﹝紹興﹞有限公司資金貸與達「公開發行公司 資 | 資金貸與之限額 (仟元) · 迄事實發生日為止，資金貸與餘額 (仟元) · 迄事實發生日為止，資金貸與餘額占公開發行公司最近期財 · 原資金貸與之餘額 (仟元) |
| 14 | 14 | 11 | skipped | 本公司之子公司EDISON OPTO USA CORPORA · 公告本公司董事會決議115年第三季盈餘分配發放現金 | 發放股利種類及金額 · 股利所屬年度 · 股利所屬期間 · 盈餘分配之現金股利 |
| 22 | 15 | 4 | passed → debt | 本公司依「公開發行公司資金貸與及背書保證處理準則」第二十五  · 本公司代子公司騰輝電子股份有限公司 依「公開發行公 司資金貸 | 背書保證之限額 (仟元) · 原背書保證之餘額 (仟元) · 本次新增背書保證之金額 (仟元) · 被背書保證公司實際動支金額 (仟元) |
| 21 | 7 | 1 | skipped | 代子公司申華化學工業有限公司公告解除 董事競業禁止之限制 · 代子公司台橡（南通）實業有限公司公告解除 董事競業禁止之限制 | 經理人如有對該大陸地區事業從事投資者，其投資金額及持 · 董事如有對該大陸地區事業從事投資者，其投資金額及持股 |
| 43 | 5 | 2 | skipped | 代子公司「中國化學製藥股份有限公司」董事會通過對 財團法人王 · 代子公司「中國化學製藥股份有限公司」董事會通過 2027年「 | 捐贈金額 |
| 35 | 2 | 5 | skipped | 本公司買回庫藏股執行完畢 · 公告本公司買回庫藏股期間屆滿執行情形(更正實際買回期間) | 本次平均每股買回價格 (元) · 原預定買回股份總金額上限 (元) · 原預定買回區間價格 (元) · 本次已買回股份總金額 (元) |
| 17 | 3 | 3 | skipped | 代子公司台橡（南通）實業有限公司公告股東臨時會 召開事宜 · 公告本公司董事會決議召開115年第二次股東臨時會 | — |
| 18 | 5 | 0 | skipped | 玉山金控代子公司三商美邦保險代理人股份有限公司公告 董事會代 · 代子公司申華化學工業有限公司公告股東臨時會 重要決議事宜 | — |
| 26 | 4 | 1 | skipped | 公告本公司之子公司"好漾生活股份有限公司"之線上商店 委外服 · 公告子公司安永生活事業股份有限公司電商平台委外服務 商發生資 | 可能獲得保險理賠之金額 |
| 10 | 2 | 2 | skipped | 公告本公司董事會決議通過與聯貸銀行團簽訂聯合授信 合約 · 代重要子公司ShunYun Technology Holdi | — |
| 16 | 1 | 3 | skipped | (補充115/3/13公告)本公司董事會決議不繼續辦理114 · 公告本公司不繼續辦理前經114年12月12日股東臨時會通過之 | 本次變更對股東權益之影響 |
| 7 | 3 | 0 | skipped | 公告本公司因會計師事務所內部輪調更換會計師 · 玉山金控代子公司三商保代公告變更會計師事務所及簽證會計師 | — |
| 3 | 1 | 1 | skipped | 公告本公司太子廠部份產線暫時停產事宜。 · 本公司業務大幅縮減，擬依法辦理大量解僱勞工並提報 「解僱計畫 | 出租之公司廠房或主要設備占總資產比例 · 質押之資產占總資產之比例 · 質押之資產占總資產比例 |
| 47 | 1 | 0 | skipped | 公告本公司115年第三季合併財務報告因適用 T-IFRSs及 | 本國上市有價證券財務資訊之差異項目及金額 · 境外發行有價證券財務資訊之差異項目及金額 |
| 1 | 1 | 0 | skipped | 公告說明本公司民國115年2月23日公司債到期尚未償還，本月 | 喪失債信之金額 |
| 40 | 1 | 0 | skipped | 本公司因有重大訊息待公布，經證交所同意自115年11月10日 | — |
| 28 | 1 | 0 | skipped | 公告本公司客戶 THE CHILDREN’S PLACE,  | 債權種類或背書保證金額及其所占資產比例 |
| 36 | 1 | 0 | skipped | 公告本公司庫藏股註銷完成變更登記事宜 | — |
| 52 | 0 | 1 | skipped | 公告本公司董事會決議通過因子公司蘇州冠禮科技股份有限 公司擬 | 對公司或子公司財務、業務或股東權益具重大影響之承諾事 |
| 44 | 0 | 1 | skipped | 公告本公司獨立董事對薪酬委員會決議事項表示反對意見 及對董事 | — |

