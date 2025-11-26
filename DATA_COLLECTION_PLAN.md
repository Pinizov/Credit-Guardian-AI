# Credit Guardian Data Collection Plan

## 1. Current Ingestion Coverage
Existing implemented scrapers:
- `ApisBgScraper` (consumer authority site, currently returns empty JSON: needs selector refinement and confirmed endpoints).
- `CielaNetScraper` (priority consumer protection laws; structure extraction incomplete as `full_text`, `articles`, `chapters` are empty – improve selectors).
- `LexBgScraper` (priority laws search; currently returns empty list – search logic likely failing due to selector changes).

Existing stored datasets (`data/`):
- `apis_bg_data.json` (violations + blacklist arrays empty).
- `ciela_net_laws.json` (3 laws stub metadata without text).
- `lex_bg_laws.json` (empty).

Database schema coverage:
- Regulatory & legal: `LegalDocument`, `LegalArticle` (structured law storage), `ConsumerCase` for precedent / enforcement.
- Market actors: `Creditor`, related risk artifacts: `Violation`, `UnfairClause`, `CourtCase`, `CreditProduct`.
- Contract analysis & user artifacts: `Contract`, `Fee`, `ContractViolation`, `Complaint`, `Payment`.

## 2. Target Data Domains & Purpose
| Domain | Purpose | Downstream Use |
|--------|---------|---------------|
| Statutory & regulatory texts | Ground truth for legal reasoning | Clause detection, compliance mapping, embeddings |
| Enforcement actions & penalties | Risk profiling of creditors | Risk score, violation prediction |
| Court decisions (consumer credit / unfair clauses) | Precedent reasoning | Legal argument generation |
| Registered financial institutions (banks, non-bank lenders) | Entity resolution | Linking contracts, license verification |
| Credit product offers (APR, fees) | Benchmark + anomaly detection | GPR calculations, illegal fee detection |
| Macro indicators (interest rates, inflation, unemployment, wage growth) | Contextual risk & affordability | Dynamic risk scoring, model features |
| Monetary policy rates (BNB base interest, ECB rates) | APR validation, projections | Interest stress testing |
| Consumer complaints (KZP) | Early warning signals | Pattern mining, classifier training |
| Corporate registry metadata (ownership, status) | Creditor health | Risk model enrichment |
| EU directives & regulations (consumer credit harmonization) | Compliance alignment | Legal gap analysis |

## 3. Priority Public Sources (Phase 1)
| Source | Data | Access | Update Cadence | Integration Notes |
|--------|------|--------|----------------|-------------------|
| Bulgarian National Bank (BNB) | Base interest rate, monetary stats | HTML tables / XLS / CSV | Monthly / ad-hoc | Normalize time series; store in `economic_indicators` table (to add). |
| National Statistical Institute (NSI) | CPI, wage, unemployment, demographics | Open Data API / CSV | Monthly / Quarterly | Create generic `TimeSeriesIndicator` model. |
| Consumer Protection Commission (KZP) | Complaints, decisions, blacklist | HTML pages / PDF | Weekly | Extend `ConsumerCase` (authority = KZP). |
| APIS.bg (existing) | Violations, decisions | HTML | Weekly | Fix selectors & map to `ConsumerCase` and `Violation`. |
| lex.bg + ciela.net (existing) | Laws, amendments | HTML | As published | Improve article/chapter parsing into `LegalDocument` & `LegalArticle`. |
| Trade Register (registryagency.bg) | Company metadata (Bulstat, status) | HTML (captcha risk) / paid API | Daily / On demand | Consider semi-manual enrichment; cache responses. |
| BNB Register of Non-Bank Financial Institutions | Licensed entities | HTML | Monthly | Populate/refresh `Creditor` records. |
| EUR-Lex | EU directives (e.g. CCD) | REST API / XML | As amended | Tag `LegalDocument` with jurisdiction='EU'. |
| FSC (Financial Supervision Commission) | Administrative measures (if relevant) | HTML | Weekly | Map to `ConsumerCase`. |
| ECB Statistical Data Warehouse | Reference interest rates | API / CSV | Daily | Align timestamps & currency. |

## 4. Gap Analysis Summary
Immediate gaps: lack of actual law texts, missing violations data, no macro/economic feed, no creditor registry normalization, absence of court decision ingestion.
Risk scoring currently relies only on local violation heuristics; needs integration of macro hooks + enforcement density per period + product anomalies.

## 5. Data Quality & Governance Principles
- Provenance tracking: every record carries `source`, `source_url`, `scraped_at` ISO timestamp.
- Idempotent ingestion: use natural keys (e.g., decision number + authority; law title + document number) to avoid duplicates.
- Versioning for laws: retain previous text when amendments detected (delta diffing later phase).
- Normalization: monetary values stored as float BGN; store foreign currency fields with explicit currency code if present.
- Freshness monitoring: per-source last successful scrape timestamp logged.
- Validation: basic schema checks (non-empty text, date parse success) before DB commit.

## 6. Phased Implementation Roadmap
Phase 1 (Week 1-2):
- Fix existing law scrapers (selectors for text, articles).
- Implement KZP complaints / decisions scraper.
- Implement BNB interest rate + macro indicators base (BNB + NSI).
- Introduce base scraper interface & centralized logging.

Phase 2 (Week 3-4):
- Court decisions ingestion (target consumer credit cases) – start with public summaries.
- Trade Register metadata enrichment for existing creditors.
- EUR-Lex directive fetch + tagging (link Bulgarian transpositions).
- Product offer scraper (collect advertised APR vs calculated GPR).

Phase 3 (Week 5+):
- Amendment diff tracking for laws.
- Historical backfill of macro series.
- Advanced NLP tagging of articles (themes, obligations, risk categories).
- Quality dashboards and anomaly detection (e.g., sudden penalty surge).

## 7. Proposed Database Extensions
New tables (to define later):
- `economic_indicators` (id, indicator_code, indicator_name, date, value, unit, source).
- `credit_offers` (id, creditor_id, product_name, apr_stated, apr_calculated, fees_json, scrape_date, source_url).
- `source_status` (id, source_name, last_success, last_error, error_count, enabled).

## 8. Standard Scraper Interface (Design)
Fields:
- `name`, `base_url`, `session`.
Methods:
- `fetch_raw(...)` – network call with retries.
- `parse(...)` – convert raw to structured items.
- `transform(...)` – map to canonical schema.
- `save_to_json(data, path)`.
- `persist(data, session)` – upsert into DB.

## 9. Next Concrete Actions
1. Add `base_scraper.py` with abstract class + retry/backoff.
2. Scaffold placeholder scrapers: BNB, NSI, KZP, EUR-Lex, Trade Register.
3. Enhance existing scrapers to implement interface.
4. Create migration for new tables (economic indicators & credit offers).

## 10. Risks & Mitigations
| Risk | Mitigation |
|------|------------|
| Selector breakage | Centralized CSS/XPath patterns & tests |
| Rate limiting / blocking | Respect delays, random jitter, rotating User-Agent |
| Captcha / anti-bot (Trade Register) | Fallback to manual or purchase API access |
| Incomplete law text extraction | Multi-strategy DOM selection + size threshold checks |
| Currency / numeric parsing errors | Central parsing utility with locale (BG) awareness |
| Time zone inconsistencies | Store all timestamps UTC ISO; convert on presentation |

## 11. Source Prioritization Score (Heuristic)
Scoring dimensions: Impact (1-5), Availability (1-5), Effort (1-5 inverse), Freshness Need (1-5). Weighted formula: 0.4*Impact + 0.2*Availability + 0.2*(6-Effort) + 0.2*FreshnessNeed.
High priority list: KZP decisions, BNB rates, NSI CPI.

## 12. Compliance & Ethical Considerations
- Only scrape publicly accessible, non-personal data; anonymize any incidental PII.
- Respect robots.txt and legal terms; where disallowed, seek API or manual feeds.
- Document data lineage for auditability.

---
Generated November 24, 2025.
