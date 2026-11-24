# ATLAS GitHub Research Intake

Research packages are kept under `docs/research/intake/` as JSON source records on the dedicated `atlas-research-data` branch. A GitHub Actions workflow watches additions and updates, obtains a short-lived GitHub OIDC identity token, and posts each package to `/research/github-intake`. It imports new or changed JSON incrementally and can reconcile every archived JSON through manual dispatch or a workflow-definition update.

## Trust boundary

- No ATLAS automation key or API token is stored in GitHub.
- The API verifies the GitHub OIDC signature against GitHub's published JWKS, then checks issuer, audience, repository, branch, and exact workflow identity before accepting findings.
- Intake is idempotent by stable `source_id` (or source URL fallback); repeated pushes are reported as duplicates.
- Every successful intake creates or updates a `research_intake_batch` audit record in the API, linking its findings to the JSON batch, GitHub path/commit, Actions run, and inserted/duplicate counts.
- Accepted findings remain unverified until source review. RIA candidates stay in triage and cannot be promoted to confirmed results automatically.

## Data delivery

The API database is the runtime source for the Pesquisa screen in the web and mobile clients. Once intake completes, the clients can show the records after refresh; research data does not require rebuilding the frontend. GitHub retains the JSON audit trail. Render deploys application code from `atlas-1.9-possible-worlds`; commits to `atlas-research-data` do not rebuild the site or app.

The GitHub Actions workflow requires `id-token: write` and is limited to the trusted workflow and branch. No third-party webhook secret is required. Scheduled ChatGPT tasks publish their resulting JSON package to this branch; the workflow then imports it automatically. A successful GitHub commit is not by itself proof of API ingestion; check that the Actions run succeeds and the package appears in `GET /research/packages` before reporting completion.

The Pesquisa screen shows recent package receipts and links back to the source JSON and workflow run. Owners can list packages with `GET /research/packages`, retrieve one package and its findings with `GET /research/packages/{batch_id}`, and replay an archived package through the owner-authenticated `POST /research/packages/{batch_id}/replay` route. For an initial or periodic backfill, use the GitHub Actions “ATLAS Research Intake” workflow's manual dispatch.

## Current initial packages

- `atlas-vigilancia-critica-2026-11-19T1924.json`
- `atlas-fechamento-estrategico-2026-11-19.json`
