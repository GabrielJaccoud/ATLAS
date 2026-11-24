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
- `POST /research/intake`: owner-authenticated manual or JSON-package intake.
- `POST /research/automation/intake`: scheduled producer intake using `X-Atlas-Automation-Key`.
- `POST /research/investigate`: immediate web investigation from Talk or Pesquisa; requires the OpenAI API web-search capability.
- `POST /research/automation/daily-run`: scheduled native web research, ingestion, daily-plan generation, and email when available; requires the automation key and an OpenAI API key.
- `POST /research/daily-plan`: manually consolidate current inputs.
- `PATCH /research/goals/{goal_id}`: update goal progress.
- `POST /research/daily-plan/{plan_id}/email`: send the page link by email.

Set `ATLAS_RESEARCH_AUTOMATION_TOKEN` only as a private Render service variable. The Render cron producer uses the same value; never put it in frontend configuration, a URL, a report, or source control.

## ChatGPT scheduled reports

The five scheduled ChatGPT research automations retain their individual reports and append an importable JSON envelope. They are instructed to archive nonempty reports and packages in the dedicated GitHub data branch. GitHub Actions exchanges a short-lived OIDC identity for authenticated ingestion into the Atlas API; its run must succeed before an API import is claimed. If the GitHub connector is unavailable to a scheduled run, the JSON remains available for manual import in Pesquisa. This path does not use a paid Render cron.

The API endpoint and runner for a native ATLAS daily run are implemented. The Render cron could not be provisioned because Render returned HTTP 402 and requires a payment method on the account. Until that requirement is resolved, there is no direct scheduled API run; ChatGPT task results enter through JSON import. When provisioned, the Render cron uses `web_search`, writes to the API, and can email the result link when SMTP is configured.

## Persistent website pairing

Owner sessions are stored in the paired browser and renewed silently on app startup, manual refresh, and every 30 days while the page remains open. The API issues rolling 365-day sessions. This keeps the browser paired between normal visits; pairing is needed again only after the local session is cleared/disconnected or remains unused beyond its validity. “Desconectar” removes the browser's saved session.

## Historical context in scheduled reports

Use historical context when it helps explain a mechanism, trend, or change in interpretation. Compare the new observation with a dated precedent, baseline, or earlier phase; say what is similar and what differs. Treat historical analogy as a way to generate questions, not proof of a causal link. Distinguish when an event occurred, when it was published, and when ATLAS ingested it if those dates differ materially.
