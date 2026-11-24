# ATLAS Research and Production Central

The Pesquisa screen is the operational inbox for new reports, hypothesis links, daily goals, and RIA triage. Manual intake and scheduled producers use the same finding schema and deduplicate records by stable source identity.

New findings may include structured teaching fields: `what_happened`, `background`, `why_it_matters`, `implications`, `glossary`, `recommended_action`, and `limits`. The web screen renders these separately so a reader can distinguish the observed result from context, inference, possible consequences, next steps, and limitations. Old records remain valid because every field is optional.

Research routines should continuously scan neuroscience, optogenetics and neurotechnology; computing and AI, including biologically inspired methods; and biotechnology, including genome editing, organoids and synthetic biology. Report only substantive, sourced updates. State whether evidence comes from cells, animals, observational work, or human clinical studies; laboratory feasibility is not clinical proof.

Every report should explain unfamiliar abbreviations at first use and include a short glossary. Each alert should teach: what changed, how it is known, what happened before, what is fact versus inference, why it matters to ATLAS, and what concrete safe step could reduce uncertainty or produce a useful result. If no justified action exists, say “monitor” and define a measurable trigger.

## Daily flow

1. A scheduled ATLAS run searches current web sources for changes relevant to the ministry registry, open research questions, and hypotheses stored in `research_hypothesis` or `hypothesis` records.
2. Each finding retains its URL, publication date when available, source type, ministry, hypothesis references, confidence, priority, and evidence class. Ingestion does not itself validate the claim.
3. The daily plan routes up to three priority findings to the relevant ministries and proposes source-apuration, hypothesis-comparison, or RIA/engineering-reverse-engineering goals. Each goal has a deliverable and completion criterion.
4. RIA candidates remain at `source_triage` until mechanism, unknowns, alternatives, and a discriminating test are documented. No result is promoted automatically to a confirmed hypothesis or scientific article.
5. Goal status is tracked in the daily plan. If SMTP is configured, a run with new findings sends Gabriel a short email with a link to `/?screen=Pesquisa`.

## API

- `GET /research/central`: findings, hypothesis records, backlog, latest plan/run, and configuration state.
- `GET /research/packages`: paginated package ledger with producer, batch, archive path/commit, workflow run, counts, and API ingestion status.
- `GET /research/packages/{batch_id}`: one package and its findings.
- `POST /research/packages/{batch_id}/replay`: owner-authorized, idempotent reprocessing of a supplied package with the matching batch ID.
- `POST /research/intake`: owner-authenticated manual or JSON-package intake.
- `POST /research/github-intake`: GitHub Actions intake, authenticated by short-lived OIDC and restricted to the ATLAS repository, branch, and workflow.
- `POST /research/automation/intake`: optional direct scheduled intake using `X-Atlas-Automation-Key`.
- `POST /research/investigate`: immediate web investigation from Talk or Pesquisa; requires the OpenAI API web-search capability.
- `POST /research/automation/daily-run`: scheduled native web research, ingestion, daily-plan generation, and email when available; requires the automation key and an OpenAI API key.
- `POST /research/daily-plan`: manually consolidate current inputs.
- `PATCH /research/goals/{goal_id}`: update goal progress.
- `POST /research/daily-plan/{plan_id}/email`: send the page link by email.

`ATLAS_RESEARCH_AUTOMATION_TOKEN` is only needed for an optional direct Render producer. The GitHub Actions OIDC path does not need that secret and is the standard route for the five ChatGPT routines.

## ChatGPT scheduled reports

The five scheduled ChatGPT research automations retain their individual reports and archive a Markdown report plus an importable JSON envelope for every completed run, including runs with no new findings. Empty runs use `findings: []` and remain explicitly visible in the API ledger as `completed_no_findings`. The GitHub Actions workflow imports each changed package automatically and can reconcile the full JSON archive after a workflow update or manual dispatch. The API records one audit entry per package, links its findings to the batch, and stores the GitHub report/JSON paths, commit, and workflow run. A successful commit alone is not proof of ingestion: the workflow must finish successfully and the package must appear in the API ledger. If the GitHub connector is unavailable to a scheduled run, the automation must report the failure and leave the JSON/report available for recovery.

## Package audit and management

`research_intake_batch` is the API ledger for package-level status. Each successful intake records the producer, batch ID, generation and ingestion times, ingestion channel, archive path and commit, workflow run URL, received/inserted/duplicate counts, and stable finding IDs. Finding records keep their source URL and are marked unverified until apuração. Repeated imports are idempotent by stable source identity and update the package's latest ingestion record rather than creating duplicate findings.

The Pesquisa screen displays the package count and recent import ledger. Owners can query packages and findings through the API routes above, or replay an archived JSON package through the owner-authenticated route. New JSON pushes are imported continuously; a full archive reconciliation is available through GitHub Actions.

The API endpoint and runner for a native ATLAS daily run are implemented. The Render cron could not be provisioned because Render returned HTTP 402 and requires a payment method on the account. Until that requirement is resolved, there is no direct scheduled API run; ChatGPT task results enter through JSON import. When provisioned, the Render cron uses `web_search`, writes to the API, and can email the result link when SMTP is configured.

## Persistent website pairing

Owner sessions are stored on the paired device and renewed silently on app startup, manual refresh, and every 30 days while the page remains open. The API issues rolling 365-day sessions. This keeps the browser or installed Android app paired between normal visits; each separate browser profile or new app installation still needs a one-time owner-code pairing. Pairing is needed again only after the local session is cleared/disconnected or remains unused beyond its validity. “Desconectar” removes the device's saved session. The website, PWA, and Android package share this frontend and the same Render API; Android uses its own on-device storage.

## Historical context in scheduled reports

Use historical context when it helps explain a mechanism, trend, or change in interpretation. Compare the new observation with a dated precedent, baseline, or earlier phase; say what is similar and what differs. Treat historical analogy as a way to generate questions, not proof of a causal link. Distinguish when an event occurred, when it was published, and when ATLAS ingested it if those dates differ materially.
