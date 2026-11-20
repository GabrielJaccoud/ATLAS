# ATLAS Radar Matinal — 2026-11-20

Corte: 2026-11-20T09:57:47Z. Pesquisa de fontes públicas, sem execução de modelos calibrados ou leitura de sensores brutos.

## Achados
### 1. Busca de pulsares com algoritmos de reticulados acelera análise de dados Fermi
Fonte: https://science.nasa.gov/open-science/fermi-data-pulsar-discovery/
Data: 2026-11-19
Classe: primary_source; confiança editorial: 0.91; prioridade: 0.92
NASA relata descoberta do pulsar PSR J1622−7204 com método inspirado em reticulados criptográficos sobre 15 anos de dados Fermi. Comparação informada: cerca de 10 horas de CPU contra método anterior que não encontrou o sinal após esforço equivalente a 600 anos de CPU. Resultado publicado pela equipe, não reproduzido nesta execução; requer dados Fermi, código, parâmetros e benchmarks equivalentes.

### 2. Mapas lidar 3D de 1 metro para risco de incêndio na Califórnia
Fonte: https://science.nasa.gov/blogs/science-news/2026/11/18/california-wildfire-risk-3d-maps/
Data: 2026-11-18
Classe: primary_source; confiança editorial: 0.92; prioridade: 0.78
NASA relata mapa estadual 3D de resolução espacial de 1 metro derivado de lidar aerotransportado USGS 3DEP, para análise de vegetação e incêndios. Existência do método e produto documentada; desempenho preditivo sobre incêndios não validado nesta execução. Teste requer mosaicos 3DEP, perímetros de incêndio, meteorologia e controles topográficos.

### 3. Petróleo cai apesar de riscos militares; recuperação de fluxos marítimos
Fonte: https://www.reuters.com/business/energy/oil-prices-edge-higher-houthi-attacks-riyadh-raise-supply-concerns-2026-11-20/
Data: 2026-11-20
Classe: secondary_source; confiança editorial: 0.72; prioridade: 0.88
Reuters reporta Brent a US$91,03 em 20/11, queda semanal projetada de cerca de 5%, associada à recuperação dos fluxos no estreito de Ormuz. Alegações de minas e ataques permanecem sem confirmação física independente nesta apuração. Causalidade não testada: faltam AIS, volumes de exportação, seguros, preços e controles de demanda.

## Auto Research Orchestrator

**Petróleo** — H0: a sensibilidade dos retornos Brent a fluxos e risco não mudou. H1: houve mudança estrutural. Modelo: r_t = a + b1*fluxo_AIS_t + b2*estoques_t + b3*risco_t + controles + erro. Dados ausentes: AIS diário por estreito, volumes carregados, série Brent, seguros, estoques EIA, dólar, demanda e histórico de eventos. Resultado: inconclusivo. Controle negativo: corredores marítimos não afetados.

**Busca Fermi** — H0: algoritmo de reticulados não reduz custo computacional a recall e falso-positivo equivalentes. H1: reduz. Dados: Fermi LAT event files, efemérides, código e hardware comparável, benchmark cego. Resultado: positivo reportado pelos autores, replicação independente pendente.

**Lidar** — H0: variáveis 3D não melhoram previsão de severidade de incêndios sobre topografia + clima. H1: melhoram. Dados: 3DEP, polígonos de incêndios, vegetação, meteorologia, splits temporais e espaciais. Resultado: produto cartográfico confirmado, ganho preditivo inconclusivo.

## Memória histórica e Red Team
Analogias: choques do petróleo e normalizações parciais de rotas; técnicas de busca de sinais fracos em astronomia; sensoriamento lidar em gestão florestal. Analogias não são confirmação causal. Evidências contrárias: riscos físicos de transporte persistem; comparação de CPU exige equivalência de detecção; resolução espacial não assegura acurácia de risco.

## Horizontes
72h: confirmar fluxo marítimo e preços; 7d: novas observações; 30d: mudança de regime com controles; 90d: validação de modelos; 1a: persistência e desempenho fora da amostra. Probabilidades não emitidas sem calibração.

## Conhecimento & Pesquisa
Positivo: métodos e produtos NASA documentados; queda de Brent reportada. Negativo: nenhum teste reproduzido que rejeite H0. Inconclusivo: causalidade petrolífera, generalização do ganho computacional, valor preditivo do lidar. Nenhum dado físico UAP novo validado nesta pesquisa.
