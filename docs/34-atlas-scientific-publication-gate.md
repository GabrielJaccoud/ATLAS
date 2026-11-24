# ATLAS Scientific Publication Gate

## Purpose

The publication workflow is available to every ATLAS ministry and accepts work originating in research, experiments, governance, operations, or user-provided material. A submission is a research record first; it is not automatically an article or a claim of discovery.

## Epistemic classes

- `internal_hypothesis`: retained for investigation; never exportable as an established result.
- `mathematical_proof`: may support a mathematical article when definitions, assumptions, and a complete proof are recorded.
- `physical_viability`: may support a theoretical physics article when assumptions, a coherent method/model, testable predictions, references, and limitations are recorded. It must be labeled as not experimentally confirmed.
- `empirical_support`: may support an empirical article when methods, results, uncertainty, references, and limitations are recorded.
- `independent_replication`: strengthens an empirical claim when independent replication is documented; it does not remove the need to state scope and uncertainty.

## Export gate

The gate is specific to the work type:

1. Mathematical result: requires a completed proof, explicit assumptions, methods, results, references, and reviewed Portuguese and English content.
2. Theoretical physics: requires explicit assumptions, model/method, testable predictions, references, limitations, and reviewed Portuguese and English content. Physical viability is not empirical confirmation.
3. Empirical result: requires methods, results, uncertainty, references, limitations, and reviewed Portuguese and English content.

The export gate checks completeness and evidence classification. It does not certify truth, novelty, peer review, or journal acceptance. The responsible human author must check claims, sources, calculations, translations, and final PDFs.

## Bilingual output and sharing

Portuguese and English versions are separate, parallel manuscripts. Each carries the same evidence class and scope. The English text requires human review before external submission.

The API generates separate Portuguese and English PDFs for direct download. From an export-ready record, the owner can also send both attachments to the privately configured recipient from ATLAS. Direct sending requires SMTP sender credentials in the service's private environment; the interface keeps that action disabled until the sender is configured. Sending is a deliberate user action, not an automatic consequence of passing the publication gate.

## Record format

Submissions are saved as `scientific_work` records with their ministry of origin, work type, evidence level, bilingual sections, references, gate result, and creation timestamp. Revisions should preserve the original record and link to a new revision rather than silently changing a published claim.
