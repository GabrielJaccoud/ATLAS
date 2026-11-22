# ATLAS — Fechamento Estratégico — 22/11/2026, 19h BRT

## Base de comparação
Referência: fechamento de 21/11 e tópicos do Radar Matinal (Ormuz, sanções, risco energético). O relatório integral das 07h não foi recuperado nesta execução; não há deltas numéricos auditáveis.

## Achado 1 — Incêndio em Sitra, Bahrein
Em 22/11, Al Jazeera publicou imagem com crédito Reuters e nota de verificação: correspondência de arruamento e edifícios com arquivos e satélite, fumaça corroborada por outros vídeos e data compatível com comunicado do Ministério do Interior do Bahrein de 21/11. Isso sustenta a ocorrência/localização de incêndio numa instalação civil, não autoria balística ou alegações iranianas de destruição de radares. Fonte: https://www.aljazeera.com/news/2026/11/22/whats-behind-irans-escalation-of-attacks-in-the-gulf

Atores: Irã/IRGC, Bahrein, EUA, operadores civis, mediadores Qatar/Omã. Incentivos: dissuasão, barganha, proteção de bases e legitimidade interna. Segunda ordem: risco a civis, seguros, custo diplomático e pressão por retaliação. Hipóteses: H1 escalada calibrada; H2 expansão de ataques civis; H3 confusão de atribuição. Confirmar com perícia, geolocalização independente adicional e registros oficiais; enfraquecer com ausência de novos ataques e cessação verificável.

## Achado 2 — Reação financeira regional
Reuters em 22/11 reportou recuo do índice saudita de 2%, do catariano de 1,6% e do bareinita de 0,6%; aversão a risco regional e venda global coexistem. Evidência de preço, mas causalidade exclusiva da guerra não estabelecida. Fonte: https://www.reuters.com/world/middle-east/most-gulf-bourses-retreat-sporadic-attacks-continue-2026-11-22/

Atores: investidores, bancos, governos e empresas regionais. Beneficiários eventuais: posições defensivas e ativos substitutos; não prova de manipulação. Sinais: persistência do recuo, spreads de crédito, volumes e novos incidentes.

## Ormuz — continuidade, não duplicar achados de 21/11
Reuters reportou em 21/11 dois incidentes próximos a Khasab; sem identificação conclusiva de duas embarcações distintas ou autoria. Em 22/11, cobertura regional menciona novo incidente, ainda sem perícia/identificação de navio suficiente para promover a evento confirmado independente. Fontes: https://www.reuters.com/business/energy/tanker-hit-by-unknown-projectile-near-omans-khasab-ukmto-says-2026-11-21/ ; https://www.euronews.com/2026/11/22/tanker-incident-involving-military-forces-reported-in-strait-of-hormuz

## Probabilidades prospectivas
Estimativas subjetivas ilustrativas, não calibradas; eventos cumulativos desde 22/11 19h BRT:
- Novo incidente marítimo com dano corroborado em Ormuz: 72h 35%; 7d 60%; 30d 80%; 90d 91%; 1 ano 97%.
- Novo ataque com dano confirmado a infraestrutura civil no Golfo: 72h 25%; 7d 50%; 30d 73%; 90d 86%; 1 ano 94%.
- Brent registrar fechamento acima de US$ 105: 72h 5%; 7d 14%; 30d 28%; 90d 44%; 1 ano 62%.
Não há atualização matemática contra o Radar Matinal, por falta do prior preservado.

## Apuração multimodal
Geolocalização e comparação com satélite realizadas por equipe jornalística e documentadas em legenda, não reproduzidas diretamente aqui. Reuters e fontes regionais consultadas. Sem inspeção própria de SAR/óptico bruto, AIS individual, sensores ou on-chain. Nenhuma comunicação privada acessada.

## Decisões
Elevar verificação de incidentes civis, acompanhar alertas UKMTO, tráfego e seguros, mercados e mediação. Não atribuir autoria ou eficácia militar a partir de vídeo de incêndio. Testar hipóteses com observáveis independentes e conservar previsões originais para Brier Score.

## Arquivamento
Esta edição contém dois achados novos distintos do lote de 21/11. Ingestão na API só pode ser declarada após sucesso comprovado do workflow.

## JSON
```json
{
  "batch_id": "atlas-fechamento-estrategico-2026-11-22",
  "producer": "ATLAS Fechamento Estratégico",
  "generated_at": "2026-11-22T22:00:26Z",
  "findings": [
    {
      "source_id": "https://www.reuters.com/world/middle-east/most-gulf-bourses-retreat-sporadic-attacks-continue-2026-11-22/",
      "title": "Mercados do Golfo recuam após novos ataques e riscos regionais",
      "summary": "Reuters relata em 22/11 queda de 2% no índice saudita, 1,6% no catariano e 0,6% no Bahrein, em meio a ataques e aversão a risco. São movimentos de mercado publicados, não prova de que cada queda foi causada exclusivamente pelo conflito; vendas globais também pesaram.",
      "source_url": "https://www.reuters.com/world/middle-east/most-gulf-bourses-retreat-sporadic-attacks-continue-2026-11-22/",
      "published_at": "2026-11-22",
      "source_type": "news_article",
      "ministry_id": "research_evolution",
      "hypothesis_ids": [],
      "tags": [
        "Gulf",
        "markets",
        "Iran",
        "geopolitics",
        "risk"
      ],
      "confidence": 0.88,
      "priority": 0.88,
      "evidence_class": "secondary_source"
    },
    {
      "source_id": "https://www.aljazeera.com/news/2026/11/22/whats-behind-irans-escalation-of-attacks-in-the-gulf",
      "title": "Vídeo geolocalizado e corroborado de incêndio em instalação civil no Bahrein",
      "summary": "Cobertura de 22/11 apresenta imagem de incêndio em Sitra após ataque de 21/11; legenda da Reuters informa verificação do traçado viário e edifícios contra imagens de arquivo e satélite, vídeo corroborante e data alinhada ao Ministério do Interior. A verificação apoia localização e ocorrência do incêndio, mas não comprova por si só origem do projétil ou danos a radares militares alegados pelo Irã.",
      "source_url": "https://www.aljazeera.com/news/2026/11/22/whats-behind-irans-escalation-of-attacks-in-the-gulf",
      "published_at": "2026-11-22",
      "source_type": "news_article",
      "ministry_id": "research_evolution",
      "hypothesis_ids": [],
      "tags": [
        "Bahrain",
        "Sitra",
        "geolocation",
        "satellite_reference",
        "verification",
        "Iran"
      ],
      "confidence": 0.84,
      "priority": 0.94,
      "evidence_class": "secondary_source"
    }
  ]
}
```
