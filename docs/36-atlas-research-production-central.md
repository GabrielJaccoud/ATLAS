# ATLAS Research and Production Central

The Pesquisa screen is the operational inbox for new reports, hypothesis links, daily goals, and RIA triage. Manual intake and scheduled producers use the same finding schema and deduplicate records by stable source identity.

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
