# Medellín P4 official source recovery via GitHub Actions — 19 November 2026

## Existing approach reused
Reused the research-only Actions design of `recover-medellin-resolution-pdfs.yml` and `probe-medellin-historico-act-search.yml`. Added:
- [targeted Python official-origin resolver](../../scripts/recover_medellin_p4_missing_acts.py)
- [Actions workflow with push and manual triggers](../../.github/workflows/recover-medellin-p4-missing-acts.yml)

All attempts use the GitHub-hosted `ubuntu-latest` runner, official `medellin.gov.co` domains only, a browser-like Spanish-Colombia user agent, bounded network timeouts, HTML/HTTP inspection and PDF signature verification. No code accesses third-party or guessed nonofficial PDF addresses, creates artificial frequencies or modifies the GTFS generator.

## Measured results, not speculation

- [First run 44558451992](https://github.com/ColombiaTransit/gtfs-medellin-colectivos/actions/runs/44558451992): **successful workflow execution**, zero recovered PDFs, diagnostic artifact `medellin-p4-105-106-246-resolutions`.
- [Second run 44558812016](https://github.com/ColombiaTransit/gtfs-medellin-colectivos/actions/runs/44558812016): **successful workflow execution** with detailed HTTP diagnostics.
- `historico-mercurio?numero_acto=202350086596`: **HTTP 200**, 25,651 HTML bytes, **0 exact numbered PDF links**.
- `historico-mercurio?numero_acto=202150041167`: **HTTP 200**, 25,651 HTML bytes, **0 exact numbered PDF links**.
- `historico-mercurio?numero_acto=175`: **HTTP 200**, 78,913 HTML bytes, **5 candidate string matches**, **NOT proven 2017 Resolución 175**. The unqualified number 175 can coincide with unrelated documents. Year and route need crosschecking before any candidate is used.
- Two ASTREA patterns per act, `r_smmed_<short>_<year>.htm` and uppercase equivalent: **HTTP 404** for all six probes. These patterns are not successful source identifiers; this does not show the original resolution is invalid or unpublished.
- SIMM public download root: **HTTP 200, 31,191 bytes**.
- SIMM category `42-resoluciones-transporte`: **HTTP 200, 23,078 bytes** from the GitHub runner; no matching resolution-number link among the first two inspected HTML pages. The other ~274 documents are **not checked**; no claim is made that the target acts are absent from the archive.
- No validated original PDF downloaded. The exact legal headways for 105/106 and 2017 246C/246D remain unavailable.

**Diagnosis:** A general Github-runner unblock is not sufficient by itself because the archive frontends **respond with HTTP 200**; the missing act is a **search/indexing or pagination/link-resolution problem**, not a demonstrated global host IP block. The historic search for the two modern IDs may simply return the same search-form page. Don't spend more time retrying the same six nonworking ASTREA URL patterns.

## Follow-up, strictly bounded

1. Inspect the `diagnostics.json` artifact from the successful run before adding further access mechanisms. Target 2017 number 175 with actual issuance date and 246 route subject, excluding superficial `175` string hits.
2. Analyze official SIMM jDownloads category pagination and exact download entry links, or request full original technical annexes from **Secretaría de Movilidad**, using numbers `202350086596`, `202150041167` and `175/2017`.
3. If numerical source truly inaccessible, keep [operator 105/106 work windows](medellin_p4_cootransmallat_operator_daytypes_2026-11-19.csv), and [historical 246 DIRECTA 2015 values](medellin_p4_246_directa_2015_official_daytypes_2026-11-19.csv) as separately qualified, without inventing later 246C/246D figures.
4. Continue with other source-specific P4 acts if required; do not reopen P1/P2/P3 or use Moovit.

Current three-daytype coverage remains **118/252**; previously modelled 069 headways and the GTFS generator were untouched.
