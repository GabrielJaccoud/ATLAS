# ATLAS Ciência Interna — 22 novembro 2026

## Novo resultado: processamento não equivale a consciência
Fontes primárias: https://www.nature.com/articles/s41586-026-10448-0 ; https://www.nature.com/articles/s41593-026-02220-4 ; https://www.nature.com/articles/s41598-026-50911-6.

**CI-004**: H0: métricas neurais refletem processamento, sedação e artefatos musculares; H1: dinâmica recorrente e integração predizem relatos conscientes além de variáveis motoras; H2: campo neural causal adicional; H3: proto-consciência universal (ontologia sem previsão exclusiva ainda). Experimentos publicados mostram processamento semântico sob anestesia, modelos adversariais e confusão por EMG; nenhum confirma H2/H3.

Modelo: X=complexidade EEG, Z=estado fisiológico/EMG, Y=relato; distinguir P(Y|X,Z) de P(Y|do(X),Z). Experimento mínimo: dados EEG/EMG com despertar e relatos cegos, validação externa por participante, permutação temporal, controle de sedação e pré-registro. Falha: ganho preditivo desaparece após ajuste EMG; inconclusivo: falta de relatos válidos.

**Teste computacional sintético** (100000 observações, seed 221126): Z binário comum; X e Y concordam independentemente com Z em 85%. Concordância observacional X/Y = 74.231%, mas após randomizar X = 49.953%. Resultado demonstra que predição não prova causalidade. Não é experimento humano nem atualização de evidência.

**CI-005**: binomial exato H0 p=.25 H1 p=.30: n=400 limiar >=115, alfa=0.0486168, poder=0.724195; n=800 limiar >=221, alfa=0.0482264, poder=0.934651. Esses valores corrigem aproximações de edições anteriores; não são evidência psi.

**CI-006/CI-001**: pares radicais e UPE permanecem programas separados de comunicação e consciência; requerem controles ópticos/EM e dados primários. Fenômenos psi, mediunidade, OBE, tradições, Gaia, Schumann, geobiologia e proto-consciência permanecem no mapa de hipóteses, sem promoção epistemológica nesta edição.

## RIA e engenharia reversa
1. **RIA-04 (modelar/testar):** classificador de consciência resistente a EMG e confusão motora. Fontes: estudo de bloqueio neuromuscular 2026 e modelo adversarial 2026. Entradas EEG/EMG/estado clínico, saída probabilidade calibrada de relato; componentes documentados: medidas EEG e modelo de campo neural; inferência ATLAS: pipeline comparativo. Teste: validação leave-one-subject-out e externo, AUC/Brier/calibração, ablação EMG, comparador espectral; sucesso apenas com ganho replicado e sem vazamento. Confiança na evidência alta; maturidade de produto conceitual.
2. **RIA-05 (observar/modelar):** dissociação entre codificação semântica e relato consciente sob anestesia. Fonte: Nature 2026 com correções. Entrada: sequências de tons/palavras, sinais intracranianos, profundidade anestésica; saída: decodificação fora da amostra; alternativa: processamento inconsciente convencional; não pressupõe consciência extracerebral. Teste mínimo: reproduzir decodificação com permutação por bloco e controle temporal. Confiança alta no relato publicado, maturidade de produto conceitual.

## Metas
Pesquisa: conferir correções e disponibilidade de dados dos três estudos. Ciência: implementar modelo causal Z->X, Z->Y e comparação observacional/intervencional. ASAS/ZAZA: separar predição, intervenção e ontologia. RIA: assimilar checklist de confusão EMG e validação externa; não assimilar teorias físicas novas.

## Pesos e limitações
Sem fatores de Bayes empíricos calculáveis com os dados disponíveis; pesos científicos inalterados. Simulação é sintética; dados individuais e condições completas dos estudos não foram reanalisados. Resultados negativos/inconclusivos devem ser registrados após experimentos reais.

## Pacote de ingestão
```json
{
  "batch_id": "atlas-ciencia-interna-2026-11-22",
  "producer": "ATLAS Ciência Interna",
  "generated_at": "2026-11-22T18:54:54Z",
  "findings": [
    {
      "source_id": "https://doi.org/10.1038/s41586-026-10448-0",
      "title": "Plasticity and language in the anaesthetized human hippocampus",
      "summary": "Registros intracranianos com Neuropixels em pacientes anestesiados encontraram discriminação de estímulos, plasticidade e informação semântica/gramatical sob anestesia geral. Evidência de processamento neural complexo sem consciência relatável; não demonstra ausência absoluta de experiência, consciência não local ou proto-consciência. Correções editoriais publicadas em junho e setembro de 2026 exigem auditoria.",
      "source_url": "https://www.nature.com/articles/s41586-026-10448-0",
      "published_at": "2026-05-06",
      "source_type": "scientific_paper",
      "ministry_id": "research_evolution",
      "hypothesis_ids": [
        "CI-004"
      ],
      "tags": [
        "consciousness",
        "hippocampus",
        "anesthesia",
        "semantic-processing",
        "RIA"
      ],
      "confidence": 0.87,
      "priority": 0.94,
      "evidence_class": "primary_source"
    },
    {
      "source_id": "https://doi.org/10.1038/s41593-026-02220-4",
      "title": "Adversarial AI reveals mechanisms and treatments for disorders of consciousness",
      "summary": "Modelo adversarial treinado em mais de 680 mil segmentos neuroeletrofisiológicos de dez segundos, validado em 565 pacientes, voluntários e animais, confronta classificadores e modelos de campo neural interpretáveis. Produz simulações e previsões de intervenção; generalização clínica e causalidade de mecanismos propostos requerem testes prospectivos independentes.",
      "source_url": "https://www.nature.com/articles/s41593-026-02220-4",
      "published_at": "2026-03-24",
      "source_type": "scientific_paper",
      "ministry_id": "research_evolution",
      "hypothesis_ids": [
        "CI-004",
        "SLCH"
      ],
      "tags": [
        "consciousness",
        "adversarial-models",
        "neural-field",
        "RIA",
        "causal-inference"
      ],
      "confidence": 0.86,
      "priority": 0.91,
      "evidence_class": "primary_source"
    },
    {
      "source_id": "https://doi.org/10.1038/s41598-026-50911-6",
      "title": "An experimental study of the effect of neuromuscular blockade on EEG-based measures of awareness",
      "summary": "Estudo experimental com seis voluntários compara EEG acordado sem bloqueio, acordado paralisado e sedado paralisado; avalia confusão por sinais musculares em métricas de consciência. Amostra pequena, cenário clínico controlado, não autoriza inferências metafísicas; mostra necessidade de controles EMG e estado motor.",
      "source_url": "https://www.nature.com/articles/s41598-026-50911-6",
      "published_at": "2026-05-02",
      "source_type": "scientific_paper",
      "ministry_id": "research_evolution",
      "hypothesis_ids": [
        "CI-004"
      ],
      "tags": [
        "EEG",
        "EMG",
        "confounding",
        "consciousness",
        "RIA"
      ],
      "confidence": 0.89,
      "priority": 0.88,
      "evidence_class": "primary_source"
    }
  ]
}
```
