# ATLAS — Fronteira do Conhecimento — 26/11/2026

Triagem pública focalizada em JMLR, DARPA, AARO, Stanford e índices científicos. Um achado incremental frente às edições visíveis; dois artigos Nature inacessíveis diretamente, excluídos. Sem confirmação extraordinária; sem benchmark operacional. Teste sintético de confundimento: quatro observações X,Y,Z = (0,0,0),(0,0,0),(1,1,1),(1,1,1) ilustram associação perfeita sem identificar direção causal; não é teste do COAT.

## COAT
- source_id: JMLR-25-2137
- title: COAT: descoberta causal assistida por modelos de linguagem
- summary: Artigo JMLR 27(229), 2026: propõe variáveis a partir de dados não estruturados e refina propostas com descoberta causal estatística; relata garantias condicionais e sete benchmarks/casos. Sem reprodução independente nesta rodada.
- source_url: https://www.jmlr.org/papers/v27/25-2137.html
- published_at: 
- source_type: scientific_paper
- ministry_id: research_evolution
- hypothesis_ids: []
- tags: ["causal-discovery","LLM","RIA"]
- confidence: 0.95
- priority: 0.92
- evidence_class: primary_source
- what_happened: Identificado artigo e PDF primários sobre COAT, novidade frente às edições visíveis.
- background: Descoberta causal depende de variáveis mensuráveis; texto livre dificulta sua definição.
- why_it_matters: Separa sugestão de variáveis de validação estatística.
- implications: Candidato para Evidence Graph e ASAS/ZAZA.
- glossary: {"COAT":"Causal representation Assistant","LLM":"Modelo de linguagem de grande escala","PAG":"Grafo ancestral parcial"}
- recommended_action: Comparar fluxo atual, extração sem feedback e COAT em dados cegos com grafos conhecidos; medir precisão, recall, custo e calibração.
- limits: Resultados dos autores; pressupostos causais e dados brutos não auditados; data diária de publicação não confirmada; sem evidência clínica ou classificada.

## Triagem e RIA
Fato público: artigo primário; capacidade relatada: sete benchmarks/casos; programa classificado: não identificado; alegação: ganho transferível; inferência: candidato ao grafo de evidências; desinformação: não identificada, risco de confundir associação e causalidade; lacuna: reprodução e baseline. H0: ganho de precisão causal <=0 sob custo equivalente. Controles: extração sem feedback, grafos sintéticos conhecidos, permutação, divisão cega. Predição: maior precisão/recall sem aumento de falsos vínculos. RIA v0.1: reconhecer COAT, investigar pressupostos e dependência do modelo, assimilar apenas em sandbox após segurança, compatibilidade, custo e ganho; rollback por desativação. Sem alteração operacional.

## Monitoramento
DARPA https://www.darpa.mil/work-with-us/communities/small-business/sbir-sttr-topics : TRIAGE-X encerrou chamada em 25/11, não demonstra capacidade. AARO https://www.aaro.mil/Next-AARO-Home-redesign/Next-Parent/Next-UAP-Report-Documents/poster/ : registros secundários com limitações, sem nova confirmação. Stanford https://news.stanford.edu/stories/2026/10/gene-editing-tool-neurological-disease : pesquisa em camundongos publicada em setembro, não novidade temporal prioritária. Nature DOI 10.1038/s41562-026-02626-x e 10.1038/s41565-026-02311-0: acesso primário falhou, não cadastrados. STAR GATE: existência histórica não prova eficácia. Sem auditoria mundial exaustiva, sem acesso classificado. Ingestão pendente de verificação.
