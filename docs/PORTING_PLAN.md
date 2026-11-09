# Plano de migração integral para Linux

## 1. Objetivo e escopo

Este projeto deve portar o **Navegador Maluco completo** do Android para Linux Mint. Não é uma extensão complementar do Firefox, nem uma coleção de scripts que substitui algumas funções do aplicativo.

O resultado pretendido é um aplicativo desktop próprio, com janela e interface de navegador, motor web integrado, abas, navegação, dados locais e o conjunto de ferramentas já existente no Android. O Firefox Extension protótipo é apenas uma experiência isolada para avaliar a reutilização de content scripts.

A referência funcional é o repositório Android. A matriz inicial está em [FEATURE_PARITY.md](FEATURE_PARITY.md).

## 2. Diagnóstico do aplicativo Android

A análise do repositório de origem identificou estes blocos:

- Interface principal e navegação em `MainActivity.kt`, com WebView, barra de endereço, menu, abas e integração com recursos do sistema.
- Política de abas, abas estacionadas, abas fixadas e agrupamento em constelações.
- Perfis WebView e política específica de cookies; diagnóstico de fluxos de autenticação Google.
- Gerenciador de extensões locais, manifests, content scripts, CSS, mensagens e armazenamento.
- Bloqueadores e controles de atenção.
- YouTube Focus, com dezenas de preferências de ocultação, bloqueio de Shorts e ferramentas de organização/estudo.
- Reprodução HTML5, serviços Media3/ExoPlayer, áudio em segundo plano, PiP e velocidade.
- Tradução de páginas por Google ML Kit, identificação de idioma, cache e restauração.
- Ferramentas de atenção, temporizadores e recompensas.

A lógica JavaScript independente de Android pode ser reaproveitada com ajustes. Kotlin/Android Activities, WebView, SharedPreferences, Media3, ML Kit Android, serviços e APIs de janela não podem ser copiados diretamente para Linux.

## 3. Hardware e requisitos não funcionais

Alvo: Linux Mint 64 bits, Intel Celeron N3060 e 4 GB de RAM.

Requisitos:
- Evitar empacotar outro Chromium completo sem justificativa medida.
- Não manter workers, timers ou serviços permanentes sem necessidade.
- Limitar o número de abas carregadas simultaneamente.
- Estacionar abas inativas e restaurar URL/título/grupo sem prometer restaurar estado impossível do DOM.
- Liberar recursos de WebView ao fechar ou estacionar abas.
- Evitar modelos de tradução grandes residentes e carregar recursos sob demanda.
- Não baixar modelos ou componentes sem consentimento e informação de tamanho.
- Medir RAM, CPU, inicialização e estabilidade com cenários reproduzíveis.
- Tratar vídeo, páginas pesadas e número de abas como variáveis relevantes.

## 4. Decisão arquitetural

### Direção proposta: Tauri + WebKitGTK

A direção para a prova de conceito é Tauri sobre WebKitGTK, criando uma aplicação desktop própria. O frontend controla a interface; o backend nativo trata armazenamento, sistema de arquivos, downloads, políticas de abas e integração com recursos do Linux.

Motivos:
- Gera uma janela e uma interface próprias, como exige o escopo completo.
- Usa WebKitGTK disponível no ecossistema Linux, sem incluir um Chromium próprio como Electron.
- Permite integração nativa com menus, diálogos, downloads e arquivos.
- Mantém a camada de interface separada do núcleo de navegação e dos serviços.

Riscos e validações obrigatórias:
- WebKitGTK não é Chromium nem Gecko; diferenças de compatibilidade podem afetar sites, extensões, autenticação e reprodução.
- Tauri não fornece automaticamente um navegador completo: abas, histórico, permissões, downloads, perfis, bloqueadores e extensões exigem implementação.
- Isolamento de perfis/cookies pode ser limitado pela versão e pela API WebKitGTK empacotada no Mint.
- APIs de tradução offline equivalentes ao ML Kit Android precisam de investigação própria.
- Desempenho real deve ser medido no Celeron N3060; não presumir que Tauri será leve em qualquer cenário.

A escolha é uma hipótese arquitetural explícita, não uma comprovação de que todos os recursos são suportados. A prova de conceito deve validar motor, compatibilidade, gerenciamento de processos, consumo e empacotamento antes de consolidar a stack.

### Alternativas consideradas

| Abordagem | Avaliação |
|---|---|
| Extensão Firefox | Não atende ao requisito de navegador próprio; serve apenas como protótipo/reuso de scripts. |
| Tauri + WebKitGTK | Direção inicial para prova de conceito; janela própria e sem Chromium empacotado. |
| GTK + WebKitGTK diretamente | Alternativa de menor camada, com maior trabalho manual de interface e integração. |
| Electron | Evitar como primeira escolha no hardware de 4 GB, pois empacota Chromium e tende a elevar o consumo. |
| Qt WebEngine | Exige avaliação de memória e empacota/usa Chromium; não é a primeira hipótese. |
| Embutir Gecko/Firefox | Não há caminho simples e estável equivalente a usar Firefox como aplicativo hospedeiro; custo de integração elevado. |

## 5. Fases de execução

### Fase 0 — Especificação e inventário
- [x] Corrigir o escopo para migração integral.
- [x] Criar matriz inicial de paridade a partir do repositório Android.
- [ ] Revisar cada recurso diretamente no código de origem e registrar comportamento, dados e dependências.
- [ ] Definir critérios de aceitação e testes por recurso.
- [ ] Definir política de migração dos dados locais Android, quando tecnicamente possível.

Critério de saída: inventário revisado, sem funcionalidades conhecidas omitidas silenciosamente.

### Fase 1 — Prova de conceito do motor e shell desktop
- [ ] Validar Tauri + WebKitGTK na versão-alvo do Linux Mint.
- [ ] Criar janela principal, barra de endereço/pesquisa e carregamento HTTP/HTTPS.
- [ ] Testar navegação, redirecionamentos, histórico básico, downloads e diálogos.
- [ ] Medir memória ociosa, uma página, vídeo e múltiplas abas.
- [ ] Testar compatibilidade em sites de referência, incluindo login e reprodução.
- [ ] Documentar limitações do motor.

Critério de saída: aplicativo desktop próprio executa navegação básica de forma estável no hardware de referência.

### Fase 2 — Núcleo de navegador e interface
- [ ] Implementar abas, alternância e fechamento.
- [ ] Implementar abas estacionadas, restauração de URL/título e limite de abas residentes.
- [ ] Implementar abas fixadas e constelações/grupos.
- [ ] Implementar histórico, favoritos e preferências.
- [ ] Implementar downloads e seleção de arquivos.
- [ ] Implementar abertura de links externos, janelas auxiliares e navegação por teclado.
- [ ] Implementar armazenamento seguro e política de cookies.

Critério de saída: fluxo principal de navegação e gerenciamento de sessões funcional.

### Fase 3 — Extensões, bloqueadores e privacidade
- [ ] Portar gerenciador de extensões locais.
- [ ] Preservar formato de manifest e API `browser` onde compatível; documentar diferenças.
- [ ] Migrar content scripts e CSS.
- [ ] Portar regras de bloqueio e permissões.
- [ ] Implementar preferências de privacidade e controles de cookies.
- [ ] Recriar diagnóstico de login sem coletar credenciais, cookies, tokens, URLs completas ou conteúdo sensível.

Critério de saída: extensões e bloqueios têm ciclo de vida, permissões e testes documentados.

### Fase 4 — Atenção e YouTube Focus
- [ ] Migrar todas as opções de YouTube Focus documentadas em `YOUTUBE_FOCUS.md`.
- [ ] Preservar ocultação de feeds, Shorts, recomendações, comentários, chat, anúncios identificáveis e publicações textuais, com limites documentados.
- [ ] Preservar bloqueio de navegação para Shorts, não apenas ocultação visual.
- [ ] Migrar ferramentas de biblioteca/fila, timestamps, anotações, temporizador e velocidade por canal.
- [ ] Migrar ferramentas de atenção, modo estudo, sessões e recompensas.
- [ ] Testar mudanças do DOM e navegação SPA.

Critério de saída: controles individuais funcionam sem quebrar pesquisa, vídeos longos e reprodução manual.

### Fase 5 — Mídia e reprodução
- [ ] Portar velocidade global de reprodução para elementos HTML5.
- [ ] Implementar controles de mídia do sistema quando suportados.
- [ ] Avaliar reprodução em segundo plano.
- [ ] Avaliar player separado, janela flutuante e PiP.
- [ ] Documentar limitações de DRM, iframes, codecs e players proprietários.
- [ ] Garantir que falhas do controle de mídia não derrubem a navegação.

Critério de saída: recursos suportados no desktop possuem equivalência testada e limitações explícitas.

### Fase 6 — Tradução de páginas
- [ ] Preservar extração de texto visível, exclusões, lotes e restauração.
- [ ] Investigar motor desktop local/offline e identificação de idioma.
- [ ] Avaliar tamanho dos modelos, RAM, CPU, licenças e privacidade.
- [ ] Implementar cache e cancelamento.
- [ ] Não enviar conteúdo de páginas a serviços remotos sem consentimento explícito.
- [ ] Documentar idiomas, conteúdo não traduzível e limitações.

Critério de saída: tradução tem mecanismo escolhido, política de privacidade, consumo e cobertura testados.

### Fase 7 — Integração, migração e distribuição
- [ ] Testar instalação limpa e atualização no Linux Mint.
- [ ] Definir pacote Linux (por exemplo, .deb) após estabilizar dependências.
- [ ] Implementar exportação/importação de preferências e dados que possam ser migrados.
- [ ] Criar testes de regressão e smoke tests automatizados.
- [ ] Medir CPU/RAM em cenários fixos e publicar resultados reais.
- [ ] Documentar recursos sem paridade e justificativas.

Critério de saída: versão desktop instalável, testada e com matriz de paridade atualizada.

## 6. Critérios de aceitação globais

- O produto final abre como aplicativo próprio, sem exigir uma janela Firefox hospedeira.
- A navegação HTTP/HTTPS, abas e controles básicos funcionam.
- Cada recurso Android do inventário possui estado: implementado, parcialmente implementado, não aplicável ou bloqueado por limitação técnica.
- Recursos não são marcados como concluídos apenas por terem interface.
- Dados locais não são transmitidos sem finalidade e consentimento.
- A aplicação não registra senhas, tokens, cookies ou conteúdo sensível em logs.
- Testes de desempenho identificam versão do Mint, motor, hardware, número de abas e cenário.
- A CI valida código, empacotamento e testes automatizáveis; testes reais de navegação permanecem separados.

## 7. Fora do escopo

- Criar um novo motor de navegador.
- Prometer compatibilidade universal com todos os sites.
- Garantir que todos os recursos Android tenham API equivalente no Linux.
- Declarar desempenho ou consumo sem medições.
- Considerar a extensão Firefox atual como o produto final.
