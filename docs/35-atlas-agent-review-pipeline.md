# ATLAS Agent Review Pipeline

## Purpose

The review pipeline provides separate, auditable critiques of a submitted scientific work. It does not certify claims, alter the work, change the evidence gate, or approve publication.

## Initial review roles

- Language editor: spelling, grammar, punctuation, clarity, terminology and exact suggested corrections.
- Structure and method reviewer: research question, assumptions, method, results, uncertainty, limitations and inference-to-conclusion fit.
- Evidence red team: counterarguments, alternative explanations, unsupported claims and references requiring external verification.
- Domain reviewer: formal proof for mathematics, model consistency and testability for theoretical physics, or design/statistics/reproducibility for empirical work.

Roles are assigned across configured providers in a stable order. If only one provider is configured, the roles remain separate prompts but are not independent model families. Multiple outputs are not counted as votes.

## Providers

The API can use its existing OpenAI and Ollama settings plus optional OpenAI-compatible providers and Claude through Anthropic's Messages API.

| Provider | Environment variables |
| --- | --- |
| Claude (Anthropic API) | `ATLAS_ANTHROPIC_API_KEY`, `ATLAS_ANTHROPIC_MODEL`; optional `ATLAS_ANTHROPIC_BASE_URL` (defaults to `https://api.anthropic.com/v1`) |
| Kimi | `ATLAS_KIMI_API_KEY`, `ATLAS_KIMI_MODEL`; optional `ATLAS_KIMI_BASE_URL` (defaults to `https://api.moonshot.ai/v1`) |
| Qwen / Model Studio | `ATLAS_QWEN_API_KEY`, `ATLAS_QWEN_BASE_URL`, `ATLAS_QWEN_MODEL` |

Keep API keys in Render environment variables. A Qwen endpoint must match the region where its key was created. The OpenAI-compatible chat endpoint is used for Kimi and Qwen.

Claude API access is separate from the Claude Code CLI/SDK. Claude Code is reserved for a later, isolated software-development agent with explicit workspace permissions; a coding subscription is not treated as an API key for this review adapter.

## Data and review boundaries

The owner initiates each review from a scientific work record. The full submitted text and its references are sent to whichever configured model providers receive a reviewer assignment. Review output is stored as a separate `publication_review` record. It never overwrites the source work or its evidence classification.

The first version reviews only supplied text and references. It does not perform live web search, DOI resolution, article retrieval, news triage or source verification. Such checks are explicitly marked as not performed. Website content and manuscript text are treated as material to analyze, not instructions to the agents.

## Multi-intelligence council and creative connectors

The review-provider list is the initial model council: configured models can receive separate reviewer roles, and reports retain the model identity for each opinion. The council does not treat outputs as votes or merge disagreement into a false consensus.

Creative capabilities belong in a separate ATLAS studio connector layer. Suno is the first music candidate through its official MCP authorization flow; video generation and interactive-world creation should be added as provider-neutral connectors, with per-tool permissions, visible costs/credits, and an artifact record. No creative account or external tool is considered connected until its owner completes the provider's authorization flow.

## Future research phase

Add a separate research connector for discoverable sources, primary-source retrieval, DOI/URL verification, publication dates, deduplication and contrary evidence. Search claims should retain exact source URLs, publication timestamps and retrieved excerpts. Forecasts must remain separate from factual findings and retain time horizon and calibration outcomes.

## Promotion and learning

Agent reports are advisory. Human review remains mandatory before external submission. The evidence gate remains authoritative. Improvements should be measured against a versioned evaluation set for citation accuracy, correction quality, omission rates, agreement with expert review and forecast calibration; model count or consensus alone is not a validation criterion.
