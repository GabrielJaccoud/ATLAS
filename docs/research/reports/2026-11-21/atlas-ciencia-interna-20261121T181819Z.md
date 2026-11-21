# ATLAS Ciência Interna — 2026-11-21

## Novo achado científico efetivamente apurado

**Magnetic resonance control of spin-correlated radical pair dynamics in vivo** — Nature 651 (2026), https://www.nature.com/articles/s41586-026-10282-4; DOI https://doi.org/10.1038/s41586-026-10282-4. Autores demonstram alteração da fluorescência de proteínas vermelhas em presença de cofator flavina, usando campos estáticos e RF próximos à ressonância de spin eletrônico, tanto in vitro quanto em nematódeos C. elegans transgênicos. A interpretação de pares radicais correlacionados é apoiada por resultados experimentais, mas não demonstra magnetorrecepção humana nem fenômenos psi.

## Formalização CI-006
H0: modulação observada explicável por aquecimento, deriva instrumental ou fotofísica não magnética. H1: rendimento de reação depende de estados de spin e do campo aplicado. H2: efeitos análogos ocorrem em sistemas humanos não modificados — ainda não demonstrado.

Modelo mínimo: H = μ_B B·(g1 S1+g2 S2)+ S1·A·I + J S1·S2 + H_RF(t); observável F(B,ω,t) = F0 + κ Φ_S(B,ω,t)+ε. A equação é um modelo candidato, não ajuste aos dados originais.

Previsões: resposta espectral centrada em frequências compatíveis com parâmetros de spin; dependência de intensidade, orientação e cofactor; desaparecimento ou modificação sob controles sem flavina, sem proteína ou fora da frequência de ressonância. Controles de temperatura, fotobranqueamento, intensidade óptica e instrumentação RF.

## Teste computacional executado
Cálculo binomial exato independente para protocolo CI-005, n=400, quatro alvos: P(X>=115|p=.25)=0.04861682035; poder para p=.30=0.7241953561. Para n=800, limiar X>=221, alfa=0.04822636145, poder=0.9346509064. Trata-se de cálculo teórico, não experimento psi nem evidência de anomalia.

## RIA e engenharia reversa — oportunidades do dia
**RIA-03: sensor bioinspirado de pares radicais por leitura óptica.** Fonte primária Nature (2026), acima. Funções documentadas: proteína fluorescente vermelha + flavina, campos estático e RF, leitura óptica. Inferência ATLAS: construir gêmeo digital de curva de resposta e estimar parâmetros de Hamiltoniano; não pressupor replicação biológica. Etapa: modelar/simular. Protótipo mínimo: simulação aberta de dois spins com relaxação e ruído; comparação entre modelo ressonante e modelo térmico; sucesso se curvas sintéticas e dados públicos (quando disponíveis) discriminarem modelos sob validação fora da amostra. Recursos: Python, bibliotecas numéricas, metadados e suplementares; nenhum equipamento biológico exigido na primeira fase. Riscos: sobreajuste, parâmetros não identificáveis, extrapolação para humanos. Confiança na demonstração publicada: alta; maturidade de produto ATLAS: conceitual. Ganho informacional: alto para distinguir explicações de magnetobiologia, baixo para consciência.

## Outras ontologias e limites
Consciência fundamental/proto-consciência, mediunidade, telepatia, OBE, corpos sutis, Reiki, Ayurveda, Wu Xing, radiestesia, Gaia consciente, Schumann e SLCH permanecem hipóteses ou ontologias a decompor; esta fonte não atualiza seus pesos. Distinguir correlação, causalidade e mecanismo. ASAS/ZAZA deve registrar origem, previsão e controles; RIA deve assimilar apenas o método de comparação de mecanismos.

## Estado epistemológico
CI-006: suporte adicional para plausibilidade de mecanismo de pares radicais em sistema biológico engenheirado; nenhum Bayes factor calculável sem dados brutos e verossimilhanças especificadas. CI-005: pesos empíricos inalterados. Resultados extraordinários confirmados: zero. Falha: dados brutos e parâmetros do sistema ainda não extraídos; sem experimento físico.

## Próxima fila
1. Extrair suplementos/dados do estudo Nature, incluindo resposta por frequência, orientação e intensidade; verificar licença. 2. Implementar modelo Lindblad/pares radicais e comparar a alternativa térmica com ajuste cego. 3. Preparar protocolo CI-005 n=800 com auditoria e controle de vazamento. Ministério: research_evolution.

## Arquivamento
Este relatório e o pacote JSON são arquivos para a Central de Pesquisa; o commit não comprova ingestão na API.
