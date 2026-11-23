# ATLAS — Radar Matinal — 2026-11-23

Corte: 2026-11-23T10:03:31Z. Triagem investigativa, memória histórica e ARO/ASAS-ZAZA.

## Achado primário novo: NOAA SWPC
Boletim emitido 2026-11-23T00:30Z: maior Kp observado nas 24h anteriores 2; máximo previsto de Kp 4,00 entre 23 e 25/11; sem previsão G1+. S1+ 1% ao dia e R1-R2 10% ao dia. Fonte https://services.swpc.noaa.gov/text/3-day-forecast.txt (fonte oficial dinâmica; preservar data de emissão). Evidência primária institucional, não artigo revisado por pares. Comparado ao boletim de 22/11, houve redução do Kp observado de 3 para 2, sem alteração na conclusão de ausência de G1 previsto.

## Atualização econômica: divergência diesel x petróleo
Análise Reuters publicada 23/11 às 07:00 UTC: petróleo bruto recupera oferta, enquanto diesel permanece escasso; estoques americanos de destilados cerca de 15% abaixo da média de cinco anos; fluxos de Ormuz estimados por Kpler em 9,5 milhões b/d nos 10 dias até 19/11, contra 12,2 milhões b/d em outubro. Fonte https://www.reuters.com/commentary/reuters-open-interest/oils-iran-war-recovery-masks-stubborn-diesel-shortage-2026-11-23/. É comentário jornalístico com dados atribuídos a terceiros, não medição direta nesta execução; incluído como contexto investigativo, não como artigo científico ou finding importável sem taxonomia apropriada.

## Auto Research Orchestrator
H0 energia: diferença entre diesel e gasolina é explicada por sazonalidade e demanda, sem efeito independente da perda de refino e exportação. H1: choques de capacidade e comércio explicam parcela incremental significativa. Método: séries temporais de crack spreads, diff-in-diff com combustíveis de controle, regressão VAR com choques e change-point. Variáveis faltantes: séries diárias EIA de estoques por produto, preços spot e futuros diesel/gasolina/Brent, throughput por refinaria, fluxos Kpler/AIS e datas de ataques e manutenção. Teste causal não executado. Cálculo descritivo com números da Reuters: (12,2-9,5)/12,2 = 22,13% de redução relativa de fluxo na janela indicada; números de fontes secundárias e períodos diferentes, não inferência causal.
H0 clima espacial: boletins NOAA não superam climatologia na previsão de G1. H1: apresentam ganho. Necessários arquivo de previsões com issue-time e Kp observado definitivo em janelas comparáveis, controles sazonais. Sem Brier score executado.

## Memória histórica e controles
Comparar com crises petrolíferas de 1973/1979 e choques de refino anteriores, incluindo períodos de risco militar sem falta de diesel. Comparar previsões NOAA a anos sem tempestade. Analogias não são confirmação física.

## Registro de resultados
Positivo documental: boletim NOAA datado e valores oficiais. Positivo aritmético: diferença relativa de 22,13% nos fluxos reportados (não teste causal). Negativo: não há G1 observado no boletim de 23/11 nem previsto até 25/11. Inconclusivos: causas da escassez de diesel, robustez do fluxo Kpler, calibração NOAA. UAP: nenhuma mudança oficial nova verificada nesta triagem; sem inferência extraordinária.

## Horizontes
72h: confrontar previsão NOAA com Kp observado; 7d: atualizar estoques e fretes; 30d: montar painel diesel-gasolina; 90d: testar mudança de regime; 1a: calibração fora da amostra. Sem probabilidades próprias sem datasets.

## Estado
Este relatório registra observações e hipóteses, não execução de sensores AIS/SAR nem ingestão API.