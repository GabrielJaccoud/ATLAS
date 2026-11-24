# ATLAS — Ouvir e transcrever mídia

## Fluxo

- **Talk ao vivo:** o navegador usa a sessão Realtime autenticada do ATLAS para captar fala no microfone e receber resposta falada.
- **Arquivo:** a tela **Ouvir** aceita áudio e vídeo; a API decodifica apenas a faixa sonora, converte para WAV mono de 16 kHz e solicita transcrição ao provedor configurado.
- **Pesquisa:** a pessoa pode editar a transcrição e encaminhá-la a **Investigar na web**, levando seu conteúdo para a Central de Pesquisa.
- **Acessibilidade:** a pessoa pode ouvir a transcrição pelo sintetizador de voz disponível no navegador.

## Privacidade e limites

- Exige uma sessão ATLAS pareada e `ATLAS_OPENAI_API_KEY` configurada.
- O modelo padrão é `gpt-transcribe`; é possível defini-lo em `ATLAS_OPENAI_TRANSCRIPTION_MODEL`.
- Aceita áudio e vídeo até 512 MB, mas limita o áudio decodificado a 24 MB para a solicitação de transcrição.
- O vídeo original, o WAV temporário e a transcrição não são gravados no banco nem na pasta de artefatos. A transcrição fica apenas no estado da página até a pessoa sair ou enviá-la à pesquisa/chat.
- A chamada de transcrição envia o WAV temporário ao provedor OpenAI configurado; portanto, a API externa recebe o áudio para executar a transcrição.
- O botão de investigação envia e registra um trecho da transcrição como pergunta de pesquisa no histórico do ATLAS. Conteúdo sensível deve ser removido antes desse encaminhamento.
- A documentação atual do provedor admite MP4 como formato de transcrição, mas o ATLAS extrai e normaliza o áudio localmente para aceitar vídeos grandes e reduzir variações de codec. O endpoint atual de transcrição documenta limite de 25 MB; o áudio normalizado fica abaixo dele.

## Verificação epistemológica

Transcrição é uma representação automática sujeita a erro, nomes próprios, sotaques, ruído e idioma. Revisar o texto antes de usá-lo como fonte. Nenhuma transcrição, análise automática ou resultado de busca valida por si só as alegações do vídeo.
