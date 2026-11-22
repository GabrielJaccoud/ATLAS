# ATLAS Radar Matinal — 2026-11-22

Corte: 07:01 BRT. Triagem investigativa e Auto Research Orchestrator.

## Novidades
1. **Ciclone Xavier (NASA, 20/11)**: imagem MODIS de 17/11 02:53 UTC; intensidade estimada 195 km/h e pico estimado 220 km/h. El Niño, SST ~29 °C e baixo cisalhamento são mecanismos plausíveis, não prova de causalidade. Fonte: https://science.nasa.gov/earth/earth-observatory/the-stormy-southwest-pacific/
2. **NOAA SWPC (22/11 00:30 UTC)**: Kp observado máximo 3, previsto máximo 4.00 entre 22 e 24/11, sem G1 esperado. S1+ 1% ao dia; R1-R2 10% ao dia. Fonte: https://services.swpc.noaa.gov/text/3-day-forecast.txt

## Contexto e memória histórica
IEA Oil Market Report de 13/11 registra recomposição parcial de oferta, mas estoques terrestres baixos e custos elevados de frete/diesel. Não é achado novo desta edição: https://www.iea.org/reports/oil-market-report-november-2026. Para Xavier, eventos anteriores de intensificação rápida no Pacífico são controles históricos necessários, não confirmação do mecanismo ENSO.

## Auto Research Orchestrator
**H0-Xavier**: condicionando em SST, cisalhamento vertical, umidade, latitude, intensidade inicial e fase sazonal, o indicador ENSO não melhora a previsão de intensificação rápida. **H1**: melhora fora da amostra. Modelo: regressão logística hierárquica ou survival hazard e ensemble com validação por ano/bacia; teste negativo com ciclones que não intensificaram. Dados faltantes: best-track IBTrACS 6h, ERA5 SST/vento/cisalhamento/umidade, índice ONI diário/mensal alinhado e amostra de controles. Sem teste causal executado.
**H0-NOAA**: a previsão G1+ não melhora a taxa-base climatológica; medir Brier Score e reliability diagram após observações Kp definitivas. Faltam arquivo histórico de previsões emitidas e Kp verificado por janela. Sem teste de calibração executado.

## Registro Conhecimento & Pesquisa
**Positivo documental**: existência de observação orbital MODIS e boletim NOAA datado. **Negativo**: boletim NOAA não prevê G1 para 22–24/11, contra hipótese de alerta elevado no curto prazo. **Inconclusivo**: contribuição causal específica do ENSO à intensificação de Xavier; calibração probabilística de alertas geomagnéticos. Nenhuma analogia/simulação foi tratada como confirmação física.

## Forecast
72h: verificar Kp definitivo e evolução de Xavier; 7d: atualizar alertas meteorológicos; 30d: compilar séries IBTrACS/ERA5; 90d: benchmark cego; 1 ano: validar previsão sazonal. Probabilidades próprias não emitidas por falta de calibração.

## Proveniência
Os dois registros usam temporariamente o tipo de fonte `scientific_paper` do contrato exemplificado, mas são **documentos institucionais, não artigos científicos**. A taxonomia do importador deve ser validada antes da ingestão; não alterar a classe real da fonte. Não foram acessados sensores militares, AIS, SAR bruto ou bases externas do ATLAS.
