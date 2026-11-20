# ATLAS Research Intake Note — 19 November 2026

This note accompanies two machine-readable research packages submitted to the ATLAS intake branch. It summarizes the supplied records and proposed follow-up. The summaries were not independently re-verified during this repository import; keep their existing evidence classes and triage status until sources are checked.

## RIA-FDML-01 — maintenance planning

The Vigilância Crítica package describes NASA technical report `NASA-CR-20260010060`, about FDML and automated maintenance-procedure planning. It reports 50 procedures for 50 faults across three systems and 18 components, with reusable actions and traceability. The supplied assessment treats this as a candidate for an isolated experiment, not assimilation into ATLAS.

**Proposed next step, not yet executed:** select a small, public, non-safety-critical maintenance benchmark; compare a baseline procedure workflow with an FDML-style model on fault coverage, step correctness, traceability, and failure recovery. Require human review and predefine rejection criteria before any integration.

Source: [NASA NTRS technical report](https://ntrs.nasa.gov/api/citations/20260010060/downloads/FDML_for_Automated_Maintenance_and_Response_v1_1.pdf?attachment=true)

## Strategic close — evidence leads

The supplied close package records five leads: a NOAA/NWS Kp 5 and G1 bulletin; South Korean export concentration in semiconductors; reported changes in Russian refinery processing; FAA router installation suspension after an outage; and lower Asian gasoline margins. The original summaries explicitly limit their implications. In particular, overlapping NOAA observation windows do not establish a new local effect; reports about refining and the FAA outage do not establish cause or sabotage; regional margin data do not demonstrate a uniform global fuel surplus.

**Proposed follow-up:** retrieve archived, timestamped primary data for the NOAA bulletin; check the South Korean ministry's underlying export series; seek independent satellite or operational evidence for refinery throughput; wait for the FAA cause report; and keep the gasoline margin conclusion regional unless broader data support expansion.

Sources are listed in the accompanying JSON package `atlas-fechamento-estrategico-2026-11-19.json`.

## Intake status

Both original JSON packages remain the authoritative record of the supplied wording, confidence, priority, source IDs, and tags. API records remain `unverified` pending source review. The proposed follow-up steps above are plans, not completed measurements or experiments.
