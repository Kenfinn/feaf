# Gold set results (11 Nov 2026)

Labeller: a finance team member, 46 real announcements from 9 Nov (about 7 per type). Answer file:
the finance team's Excel answer file (internal team material, not published), CSV version at `eval/gold.csv`.
The evaluation ran without a model (rule-based reasoner), with market data from the TWSE/TPEx OpenAPI.

## Official numbers for the deck and README

These numbers were taken **before** the agent was re-tuned from the finance team's answers. They are the
honest numbers to report.

| Metric | FEAF agent | Without the checker |
|---|---|---|
| Wrong numbers published | 0/46 | 5/46 |
| Publish/hold/archive decision matches the expert | 41/46 (89%) | 15/46 (33%) |
| Signal level matches the expert (moderate profile) | 21/29 (72%) | 0/29 |
| Held for a human | 13/46 (28%) | 33/46 (72%) |

Full report: `eval/hasil/evaluasi-20261111T084547Z.md`.

Manual-work baseline from the finance team: **20–30 minutes per announcement** (25 used). For 46
announcements that equals about 1,150 minutes of analyst work. The agent processes them in
milliseconds per announcement without a model.

## What the differences revealed

1. **Bug: a loss read as a profit.** Taiwan reports write negative numbers in parentheses, for example
   `(339,123)`. The parser read them as positive, so 29 of 177 loss-making quarterly reports
   showed up as profits. Found by a finance team member through case 6535.
2. **Bug: share counts in 仟股 (thousand shares) were not read**, and neither were the private-placement share label (私募股數)
   and the employee stock option label (認股權行使…新股總數).
3. The debt-ratio threshold for quarterly reports was too loose: the finance team flagged 55–58%.
4. A fund loan under article 23 at 47% of equity was flagged by the finance team. The regulatory limit is about 40%.
5. Article 20 transactions with a 100% subsidiary were archived by the finance team: no cash leaves the group.

## Calibration applied (approved by the team lead, 11 Nov)

| | Change | File |
|---|---|---|
| Bug 1 | Numbers in parentheses = negative | `app/agent/sinyal.py` (`_f`) |
| Bug 2 | Units 仟股/萬股/張, private-placement share and employee option labels | `app/agent/sinyal.py` (`_lembar`) |
| a | Debt ratio: conservative 40%, moderate 50%, aggressive 65% (previously 50/60/75) | `app/ambang_profil.py` |
| b | New shares whose count cannot be read = needs attention | `app/ambang_profil.py` |
| c | Fund loan ≥ 40% of equity = needs attention, all profiles | `app/ambang_profil.py` |
| d | Article 20 with a 100% subsidiary = archive | `app/agent/screen.py` (`antar_grup`) |

After calibration, on the same 46 announcements: decision 43/46, level 29/29
(`eval/hasil/evaluasi-20261111T090230Z.md`). **These are in-sample numbers**, because they were tested
on the data used for tuning. Do not report them as accuracy. For a clean test
number, 15–20 new announcements labelled without looking at the agent's output are needed.

Remaining differences: 4749 (land purchase, finance team: publish) is held because the issuer has no valuation
model yet; 2072 (end of a lease with a related party) and 6830 (subsidiary machinery) are held,
while the finance team archived them.

Impact on the 578 local announcements: 79 quarterly reports are now "needs attention", 9 inter-group
transactions are archived, and the held count dropped from 65 to 49.

## Not yet done

- Evaluation with Gemini on the server (D5).
- A new test set of 15–20 announcements for out-of-sample numbers.
