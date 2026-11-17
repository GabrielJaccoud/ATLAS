# ATLAS 1.7.0 — Operational Awareness

ATLAS is a causal futures intelligence and research system designed to investigate the world, formalize competing hypotheses, test models, forecast outcomes and improve its own operational methods.

## Current branch

This branch introduces the ATLAS **Operational Awareness** layer: a computational self-model for goals, uncertainty, evidence coverage, module health, drift detection, checkpoints and corrective interventions.

It is operational metacognition. It does **not** claim phenomenal consciousness, sentience or subjective experience.

## Core cycle

`OBSERVE → INVESTIGATE → FORECAST → PREPARE → ACT → LEARN → SELF_CHECK`

## 1.7 capabilities

- self-state snapshots;
- goal alignment and blocked-goal pressure;
- module health scoring;
- calibrated confidence and uncertainty;
- evidence coverage and contradiction load;
- context saturation detection;
- overconfidence detection;
- deterministic SHA-256 checkpoints;
- corrective intervention recommendations;
- before/after comparison for RIA technology assimilation;
- human-review recommendation for severe drift.

## Research direction

ATLAS also maintains a broader Research Engine for causal modeling, ASAS/ZAZA, RIA/Reverse RIA, multidomain forecasting and hypothesis development.

See:

- `RELEASE_1.7.0.md`
- `docs/13-operational-awareness.md`

## Development

Python 3.12+.

```bash
python -m pip install -e '.[dev]'
pytest -q
ruff check atlas apps tests
```

The full 1.7.0 codebase is being migrated into this repository in staged, reviewable commits.
