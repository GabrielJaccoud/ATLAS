from __future__ import annotations

import os
import sys

import httpx


def main() -> int:
    api_url = os.environ.get("ATLAS_API_URL", "").rstrip("/")
    automation_key = os.environ.get("ATLAS_RESEARCH_AUTOMATION_TOKEN", "")
    if not api_url or not automation_key:
        print("ATLAS_API_URL and ATLAS_RESEARCH_AUTOMATION_TOKEN are required.", file=sys.stderr)
        return 2
    try:
        with httpx.Client(timeout=180) as client:
            response = client.post(
                f"{api_url}/research/automation/daily-run",
                headers={"X-Atlas-Automation-Key": automation_key},
            )
            response.raise_for_status()
            result = response.json()
    except httpx.HTTPStatusError as error:
        print(f"ATLAS daily research returned HTTP {error.response.status_code}.", file=sys.stderr)
        return 1
    except httpx.HTTPError:
        print("ATLAS API could not be reached.", file=sys.stderr)
        return 1

    plan = result.get("daily_plan", {})
    run = result.get("run", {})
    print(
        f"ATLAS daily research complete: status={plan.get('status', 'unknown')} "
        f"findings={run.get('finding_count', 0)} goals={len(plan.get('goals', []))} "
        f"email_sent={run.get('email_sent', False)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
