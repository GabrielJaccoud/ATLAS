# ATLAS 1.7 — Operational Awareness Layer

ATLAS 1.7 adds an explicit self-model for operational metacognition. The layer is designed to make the system aware of its **computational and epistemic state**, not to claim phenomenal or subjective consciousness.

## State vector

`S_ATLAS(t)` tracks:

- active goals and progress;
- goal priority and blockage;
- module health and error counts;
- confidence and uncertainty;
- evidence coverage;
- contradiction load;
- novelty load;
- active hypotheses and tests;
- known unknowns;
- recent errors;
- context pressure;
- checkpoints and metadata.

## Drift detectors

The engine detects goal drift, evidence gaps, contradiction overload, overconfidence risk, module degradation, blocked goals, context saturation and error accumulation.

## Interventions

ATLAS can restate goals, research missing evidence, compare competing hypotheses, lower confidence, route around unhealthy modules, replan blocked goals, checkpoint/compact context, suspend autonomous promotion and increase verification depth.

## Checkpoints

Snapshots are serialized deterministically and hashed with SHA-256 for traceability.

## Integration with RIA / ASAS

Every technology assimilated by RIA can be evaluated for its effect on the ATLAS self-state through before/after snapshots.
