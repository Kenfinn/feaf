# Financial Analysis Scope — Decisions After the 13–14 Sep Discussion

Full version: (private design canvas, not published)

---

## 1. Valuation is still built

The question that came up: if price forecasting does not need to be built, does valuation not
need to be either?

**It does.** The challenge description explicitly names *"investment models"* as a part that
must be integrated. The line is not between forecasting and not forecasting, but between
**figures the judges can trace** and figures they cannot.

| Verifiable | Not verifiable |
|---|---|
| Inputs from MOPS reports, every figure clickable to its source | "The price will rise to NT$120 next month" |
| Assumptions (growth, WACC, terminal multiple) shown on screen and changeable | An ML model that outputs a target price without readable assumptions |
| Output as a fair-value range | Buy/sell signals without explanation |
| Sensitivity analysis showing how fragile the result is | A composite score with undisclosed weights |

Three conditions that make it safe:

1. Every model input must carry a citation to its source document.
2. Assumptions must be visible and changeable — a DCF with hidden assumptions is a forecast in disguise.
3. Never output a bare "BUY". Output a fair-value range versus the market price, the
   assumptions that produce it, and what would have to happen for the conclusion to be wrong.

### Monte Carlo — the wording decides

- ❌ "There is a 72% chance this stock goes up." → a statement about the future, cannot be proven.
- ✅ "Under this distribution of assumptions, fair value exceeds the market price in 72% of 10,000 simulations."
  → a statement about the model, reproducible and auditable.

---

## 2. The two product directions must be merged

After the discussion, the team had two different products in mind:

- **Direction A** — monitoring agent: watches announcements, sends alerts. Event-triggered.
- **Direction B** — equity research agent: computes ratios and in-depth valuation. Question-triggered.

In 32 days with one technical person, both are impossible. The merge:

> **Valuation is the engine. Monitoring is the trigger.** When a material announcement arrives for
> a stock on the watchlist, the agent recalculates its valuation and tells the user whether the
> undervalued/overvalued conclusion *changed* — and which assumption shifted.

```
new announcement → pull the latest figures → recalculate valuation
  → compare with the old conclusion → [changed?] → send a cited alert
  → user reaction → tune the threshold
```

The updated scope sentence:

> "An agent that judges whether a stock price is fair from official financial reports, monitors
> new announcements, and tells investors when an event changes that conclusion — complete
> with sources and assumptions."

This also answers "why not Excel?" decisively: Excel does not know when to recalculate.

---

## 3. Analysis priorities until 16 October

| Priority | What gets built | Reason |
|---|---|---|
| **Must** | CAGR, EBIT margin, D/E, ROA, ROE, dividend payout & yield | Computed directly from report rows. Deterministic, citable, fast. |
| **Must** | Unlevered DCF 2-stage | One valuation model is enough to prove the concept. Most detailed and most defensible. |
| **Must** | Sensitivity analysis (WACC × terminal growth) | Cheap to compute, and the most convincing demo element. |
| If time allows | Exit multiple as a second terminal value, averaged with the perpetuity | Cheap to add once the DCF works. |
| If time allows | Monte Carlo | Large narrative effect, but only with the correct wording. |
| **Postpone** | SOTP | Needs per-segment data that is hard to extract from MOPS, and applies only to multi-line companies. Put it on the "future development" slide in the deck. |

### Architecture point

All of the calculations above are **deterministic calculators**, not AI output. As a result:

1. There is no hallucination risk on the figures — most of the verification problem disappears.
2. The story is actually more agentic: the agent's job is not to calculate, but to *choose* which
   analysis to run, *collect and validate* its inputs, *interpret*, and *explain*.

Financial knowledge enters as **coded tools**, not as a prompt.

---

## 4. Correcting the interview methodology

An interview plan built to justify the product plan produces weak evidence. The criterion being
scored is the *quality of need validation*, and leading interviews are easy for judges to spot.

**How to ask:**
- Start open, before mentioning any concept: "Tell me about the last time you considered buying
  a stock. What were you looking for? Where? For how long?"
- Do not say the word "ratio" until they say it first.
- Ask what made them *back out* of buying — that is usually where the real pain point is.
- Also record answers that do not fit the plan.

**Strongest evidence:** show one thing that was changed because of the interviews. One slide like
that beats ten quotes that happen to agree.

**On interviewees:** prefer people who have actually bought stocks, however small the amount.
Interviewees who have never invested answer hypothetically.

Two administrative notes: teams that do real field validation must appoint a
**field liaison**, and the interview evidence in the deck must be de-identified because the
preliminary-round judging is anonymous.

---

## 5. Short answers to other questions

**Output form — 50/50 fundamental and analytics?** Do not split by technique, split by the order
of decision-making: (1) the undervalued/overvalued conclusion with its range; (2) why — the 3–4
deciding ratios, each cited; (3) what could change it — sensitivity and the most fragile
assumption; (4) what is happening now — the latest announcements touching that conclusion.

**Fisher-Yates?** It has no place as a feature — it is a shuffling algorithm. Legitimate uses
here: shuffling the order of test questions so evaluation is not order-biased, or sampling for a
holdout test. Worth one line in the methodology, do not put it in the deck as a technique.

**Fuzzy logic?** It can be used to turn continuous ratios into labels ("healthy margin"), and
that is legitimate. But explicit thresholds do the same job, are easier to explain in Q&A, and
their origin can be cited to interviews or industry benchmarks. Use explicit thresholds first.

**The 5 different issuers.** Agree they should be from different sectors, with three added
conditions: the reports are complete and consistently formatted; at least one has a recently
published material announcement (so the monitoring demo has content); and at least one is a
multi-line company if SOTP is kept as a future plan.
