# Third-Party and AI Tool Disclosure

This document is prepared to meet Article 13 of the NAPAI AAIC 2026 competition rules.
We disclose every external resource used in the development and operation of the FEAF system:
large language models (LLMs), capital-market data APIs, open-source libraries, and
artificial-intelligence development tools.

## 1. List of Third Parties, Data Services, and Software

| Name | Type | Purpose | Data scope | License or terms of use | Verified? |
|---|---|---|---|---|:---:|
| Claude Code (Anthropic) | AI coding tool | Pair-programming assistant for writing the architecture, web routes, and tests. | Snippets of the local application source code, unit test output, and session text files. | [Anthropic Commercial Terms](https://www.anthropic.com/legal/commercial-terms): "Anthropic does not use Customer Content to train our models, unless explicitly agreed upon." | Yes |
| Antigravity (Google) | AI coding tool | Pair-programming assistant for the automatic DCF calculation, attack-resilience tests, and rule compliance. | Snippets of local source code, task instructions, and unit test execution logs. | [Google Cloud AI Terms](https://cloud.google.com/terms/service-terms): "Customer Data is not used to train models without customer permission." | Yes |
| Gemini API (Google) | Model in the application | Entity extraction from public announcement text and cross-verification against exchange documents. Uses the model `gemini-3.6-flash`, temperature 0, paid tier (with automatic backup `gemini-3.5-flash` on 429 or 5xx service errors). Also used by Ask FEAF to call tools and summarize their results; every number is checked against the tool results. | Only public MOPS announcement text and public numbers are sent. No personal data, API keys, or credentials are sent to the model. | [Google AI Studio Terms of Service](https://ai.google.dev/terms): "Content submitted to the API is processed in accordance with Google APIs Terms of Service." | Yes |
| FinMind API | Capital-market data | Fetching quarterly financial statement data of Taiwan issuers (balance sheet, income statement, and cash flow). | Stock symbols and historical public financial statement data. Access is limited by a 12-hour local cache (300 requests/hour without a token). | [FinMind Open Data](https://finmind.github.io/): "Open financial data library for academic research and personal quantitative analysis." | Yes |
| TWSE OpenAPI | Official capital-market data | Profiles of listed issuers, shares outstanding data (`t187ap03_L`), and official financial statements (`t187ap06_L_ci`, `t187ap07_L_ci`). | Public disclosure data of the regular market of the Taiwan Stock Exchange. | [Taiwan Open Government Data License](https://openapi.twse.com.tw/): "The Open Government Data License allows commercial and non-commercial reuse with attribution." | Yes |
| TPEx OpenAPI | Official capital-market data | Profile and announcement data of issuers on the OTC market (Taipei Exchange). | Public profile and disclosure data of OTC issuers. | [TPEx Open Data Terms](https://www.tpex.org.tw/web/about/opendata/): "Free public access and reproduction for financial technology innovation." | Yes |
| Official TWSE & TPEx websites (R1) | Historical market data | Fetching historical daily closing price series of stocks and the Taiwan capital-market benchmark index (TAIEX). | Public daily closing price data for the last 2 years, used to compute the official weekly beta. | [TWSE Website Terms](https://www.twse.com.tw/zh/page/terms.html): "Terms for information disclosure and publication of official Taiwan exchange market data." | Yes |
| MOPS (Market Observation Post System) | Official disclosure data | Primary citation source for financial statements and for fetching issuer announcement files. | Direct citation URL links per financial statement reporting period column and the original announcements. Downloading history is restricted to Taiwan networks. | [MOPS TWSE](https://mops.twse.com.tw/): "Official capital-market disclosure reporting system under Taiwan FSC regulation." | Yes |
| Yahoo Finance | Historical market data | Was briefly used for weekly beta in the early prototype version. | No longer used since R1; all beta estimates have been moved to the official TWSE/TPEx daily prices. | [Yahoo Developer Terms](https://legal.yahoo.com/us/en/yahoo/terms/otos/index.html): "No longer used since R1." | Yes |
| Damodaran Online (Aswath Damodaran, NYU Stern) | Academic reference data | Estimate of the Equity Risk Premium (ERP) for the Taiwan market ($5.01\%$). | One country constant for Taiwan's ERP as an input to the WACC calculation. | [Damodaran Online Data](https://pages.stern.nyu.edu/~adamodar/): "An open site for education and corporate finance analysis; free to use with citation." | Yes |
| Taiwan 10-Year Government Bond Yield | Interest-rate reference data | Risk-free rate ($R_f = 1.94\%$) for the cost of equity in the WACC calculation. | One benchmark-rate constant for the 10-year Taiwan government bond. | [Central Bank of the Republic of China (Taiwan)](https://www.cbc.gov.tw/): "Official statistics on national government bond interest rates." | Yes |
| fastapi | Web framework library | Async Python HTTP backend framework. | Local code dependency in requirements.txt. | [MIT License](https://github.com/fastapi/fastapi/blob/master/LICENSE): "Permission is hereby granted, free of charge, to any person obtaining a copy..." | Yes |
| uvicorn | ASGI server library | ASGI-interface HTTP server for running the FastAPI application. | Local runtime dependency in requirements.txt (uvicorn[standard]). | [BSD 3-Clause License](https://github.com/encode/uvicorn/blob/master/LICENSE.md): "Redistribution and use in source and binary forms, with or without modification..." | Yes |
| jinja2 | Template engine library | Template rendering engine for the HTML user interface pages. | Local rendering dependency in requirements.txt. | [BSD 3-Clause License](https://github.com/pallets/jinja/blob/main/LICENSE.txt): "Redistribution and use in source and binary forms, with or without modification..." | Yes |
| httpx | HTTP client library | Local test HTTP client for `fastapi.testclient.TestClient`. | Local test dependency in requirements.txt (only for automated tests without a network). | [BSD 3-Clause License](https://github.com/encode/httpx/blob/master/LICENSE.md): "Redistribution and use in source and binary forms, with or without modification..." | Yes |
| Swagger UI (`swagger-ui-dist`) | Library, loaded in the browser | Interactive API page at `/docs`. The script is loaded from `cdn.jsdelivr.net` by FastAPI, only on the `/docs` page. | None sent; the browser fetches the script. | [Apache License 2.0](https://github.com/swagger-api/swagger-ui/blob/master/LICENSE) | Yes |
| Google Fonts (Instrument Sans, IBM Plex Mono) | Typefaces, loaded in the browser | Fonts of every page, loaded from `fonts.googleapis.com` by `app/templates/base.html` and `app/templates/kunci.html`. | None sent by the app; the browser requests the stylesheet. | [SIL Open Font License](https://fonts.google.com/) | Yes |
| Playwright (Microsoft) | Screenshot tool | Headless browser automation for taking screenshots of web pages; not included in the server application package. | Local browser interface. | [Apache License 2.0](https://github.com/microsoft/playwright/blob/main/LICENSE): "Licensed under the Apache License, Version 2.0." | Yes |
| Mermaid | Diagram tool | Rendering data flow and system architecture diagrams in the documentation markdown files. | Local markdown diagram text syntax, not imported into the application runtime. | [MIT License](https://github.com/mermaid-js/mermaid/blob/develop/LICENSE): "Permission is hereby granted, free of charge..." | Yes |
| Humanizer skill | AI skill | Editing the writing style of the documentation to be plain, natural, and free of clichéd AI sentence constructions. | Documentation markdown text files. | [MIT License](https://github.com/blader/humanizer/blob/main/LICENSE): "Permission is hereby granted, free of charge..." | Yes |
| Anti-slop skill | AI skill | Auditing the quality of code comments and cleaning generic comment text in the codebase. | Analysis of local code text syntax. | [MIT License](https://github.com/miqdadbadjuber/anti-slop/blob/main/LICENSE): "Permission is hereby granted, free of charge..." | Yes |

---

## 2. Team Division of Labour

This table is intentionally left empty to be filled in directly by the FEAF team members:

| Part | Done by | Role of AI |
|---|---|---|

---

## 3. Personal Data Note

The TPEx issuer profile cache on the server once stored the names of officers and the contact
email addresses of companies until the fix on 10 November 2026 (commit `e4572d6`). That data
was never shown to public users. Allow-list filtering (`PROFIL_DISIMPAN`)
automatically removes those personal fields when the file is read after a deploy.
