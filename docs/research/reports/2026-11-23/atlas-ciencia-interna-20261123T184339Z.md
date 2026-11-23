# ATLAS Ciência Interna — 2026-11-23

## Resultado
Três fontes primárias examinadas; duas oportunidades RIA; nenhum efeito extraordinário confirmado. Fontes: https://doi.org/10.1093/pnasnexus/pgag048 ; https://doi.org/10.1103/4l3h-b66c ; https://doi.org/10.3389/fnins.2025.1591645.

## CI-004 / SLCH: complexidade cerebral
Estudo PNAS Nexus (2026): 5703 registros iEEG em 106 pessoas, mais 474 registros de validação. Complexidade e entropia variam entre estados de vigília, sono e anestesia. Hipóteses: H0 = marcadores acompanham estado por mudanças espectrais e artefatos; H1 = dinâmica multiescala acrescenta informação preditiva fora da amostra; H2 = mecanismo físico adicional prevê resíduo reproduzível após controles. Modelo: logit(P(estado consciente)) = alfa + beta1*entropia + beta2*complexidade + gamma*confundidores. Validação: separar participantes entre treino/teste, controlar EMG, potência espectral e medicação. Sem inferência sobre proto-consciência.

## CI-006: movimento molecular e pares radicais
Physical Review Applied (2026) apresenta modelo teórico de movimento inter-radical estruturado que pode melhorar sensibilidade magnética; não é demonstração de sensor humano. H0: movimento adiciona decoerência/ruído; H1: modulação estruturada aumenta informação de Fisher sobre direção de B; H2: efeito persiste em condições bioquímicas reais. Formalização: F(B)=E[(d log p(Y|B)/dB)^2], limite de Cramér-Rao Var(Bhat)>=1/(nF(B)). Comparar modelo estático, movimento aleatório e periódico, com ruído/relaxação. Risco: parâmetros não identificáveis.

## Auditoria da magnetorrecepção humana
Corrigendum de 25/03/2025 corrige frase metodológica; autores afirmam que conclusões não mudam. Não aumenta peso causal nem demonstra replicação. Solicitar dados brutos e pré-registro para reanálise.

## Teste computacional executado
Simulação sintética com numpy, semente 20261123, n=1000: Z~N(0,1), X=Z+eX, Y=Z+eY, erros independentes. Correlação(X,Y)=0.51097, correlação(X-Z,Y-Z)=0.03377. Demonstra confundimento em exemplo construído, não prova sobre EEG, campos ou fenômenos psi. Limite: controles reais não observam todos os confundidores.

## RIA e engenharia reversa — oportunidades do dia
1. Pipeline de complexidade intracraniana: entrada iEEG autorizado, filtragem e marcação de estados; saída classificação calibrada e validação por participante. Etapa modelar/testar; métrica Brier, AUROC e ablação de confundidores; sucesso somente se melhorar fora da amostra. Confiança na evidência alta, maturidade de produto conceitual.
2. Simulador de sensor de pares radicais: entradas parâmetros de spin, acoplamentos, campo, dinâmica molecular; saída rendimento/sensibilidade e informação de Fisher. Comparar dinâmica estruturada, estática e ruído aleatório; sucesso se robusto a variação de parâmetros e baselines; sem protótipo físico. Confiança teórica moderada-alta, maturidade de produto conceitual.

## Ontologias e limites
Consciência fundamental, proto-consciência, mediunidade, telepatia, OBE, EQM, Reiki, biofields, corpos sutis, Ayurveda, medicina chinesa, radiestesia, Gaia e consciência planetária seguem em inventário sem evidência nova nesta execução. Separar tradição, experiência, observação, mecanismo e especulação; nenhuma atualização bayesiana empírica.

## Metas
Pesquisa: localizar dados e suplementos iEEG e estudo de spin. ASAS/ZAZA: implementar controles de confundimento, teste fora da amostra e assinatura de mundo. RIA: modelar antes de assimilar. Próximos testes: pipeline iEEG, simulador radical-pair, auditoria de dados humanos. Nenhuma ingestão na API afirmada.
