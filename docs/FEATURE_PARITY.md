# Matriz de paridade funcional — Android → Linux

## Objetivo

Inventário inicial dos recursos identificados no aplicativo Android para orientar a migração integral. A lista foi montada a partir do README e das documentações de YouTube Focus, tradução e velocidade, além da estrutura e dos componentes Kotlin do repositório de origem.

**Estado inicial dos recursos no desktop:** pendente ou em avaliação. A extensão Firefox deste repositório não conta como migração do navegador.

Estados:
- **Pendente:** não portado.
- **Em avaliação:** depende de prova técnica ou API do motor.
- **Parcial:** implementação incompleta, com limitações registradas.
- **Concluído:** comportamento e testes de aceitação aprovados.

## 1. Navegação e interface principal

| Recurso Android | Requisito desktop | Estado |
|---|---|---|
| Janela principal e interface | Janela própria, barra de endereço, pesquisa, menus e controles | Pendente |
| Página inicial | Página inicial equivalente e configurável, conforme comportamento original | Pendente |
| Navegação HTTP/HTTPS | Carregar URLs, redirecionamentos, voltar, avançar e recarregar | Pendente |
| Barra de endereço/pesquisa | Interpretar URLs e consultas de pesquisa | Pendente |
| Abas múltiplas | Criar, ativar, fechar e alternar abas | Pendente |
| Política de abas | Respeitar limite e política de abas residentes | Pendente |
| Abas estacionadas | Descarregar contexto ativo e manter metadados para restauração | Pendente |
| Abas fixadas | Preservar abas fixadas e impedir descarte indevido | Pendente |
| Constelações | Criar e persistir grupos nomeados de abas | Pendente |
| Restauração de sessão | Restaurar URLs e metadados; documentar o estado que não pode ser restaurado | Pendente |
| Histórico | Persistir, consultar e limpar histórico | Pendente |
| Favoritos | Criar, editar, remover e abrir favoritos | Pendente |
| Downloads | Baixar, acompanhar progresso, cancelar e abrir arquivos | Pendente |
| Upload/seleção de arquivos | Diálogo desktop integrado às páginas | Pendente |
| Janelas auxiliares | Política segura para pop-ups e novas janelas | Pendente |
| Links externos | Abrir aplicativos externos com política adequada | Pendente |

## 2. Perfis, cookies e privacidade

| Recurso Android | Requisito desktop | Estado |
|---|---|---|
| Perfil Google isolado (quando suportado pelo WebView) | Isolamento real de cookies/cache/storage ou limitação documentada | Em avaliação |
| Política seletiva de cookies de terceiros | Regras por domínio sem habilitação global indiscriminada | Pendente |
| Compatibilidade de login Google/X | Testar fluxos e documentar limitações do motor | Pendente |
| Diagnóstico de login | Relatório local mínimo, sem credenciais, tokens, cookies, e-mails ou URLs completas | Pendente |
| Limpeza de dados | Limpar cookies, cache, histórico e dados por escopo | Pendente |
| Permissões de sites | Política para câmera, microfone, localização, notificações e pop-ups conforme suporte | Pendente |

## 3. Extensões e bloqueadores

| Recurso Android | Requisito desktop | Estado |
|---|---|---|
| ExtensionManager | Instalar, habilitar, desabilitar e remover extensões locais | Pendente |
| Manifest local | Preservar campos suportados e validar versão/formato | Pendente |
| Content scripts JavaScript | Executar nos domínios e momentos declarados | Pendente |
| CSS de extensão | Aplicar e remover estilos com ciclo de vida previsível | Pendente |
| browser.runtime.sendMessage | Mensageria validada entre extensão e aplicativo | Pendente |
| browser.storage.local | Armazenamento isolado por extensão, com limites | Pendente |
| Bloqueador X/Twitter | Portar regras e opções do bloqueador | Pendente |
| Outros bloqueadores | Inventariar regras no código e preservar comportamento | Pendente |

## 4. Atenção e YouTube Focus

As preferências abaixo estão documentadas no YOUTUBE_FOCUS.md do repositório Android.

| Recurso | Requisito desktop | Estado |
|---|---|---|
| Ocultar feed da página inicial | Preferência individual | Pendente |
| Redirecionar página inicial para inscrições | Aplicar somente na raiz, preservando links diretos | Pendente |
| Ocultar Explorar e Em alta | Preferência individual | Pendente |
| Ocultar Mais do YouTube | Preferência individual | Pendente |
| Ocultar blocos irrelevantes da pesquisa | Preferência individual | Pendente |
| Ocultar aba e vídeos Shorts | Ocultação por contexto | Pendente |
| Bloquear navegação para /shorts/ | Bloqueio de navegação, não apenas ocultação visual | Pendente |
| Desativar autoplay | Controle quando suportado pelo player | Pendente |
| Ocultar mural de vídeos no encerramento | Preferência individual | Pendente |
| Ocultar cartões e anotações | Preferência individual | Pendente |
| Ocultar barra lateral | Preferência individual | Pendente |
| Ocultar recomendações | Preferência individual | Pendente |
| Ocultar chat ao vivo e playlists laterais | Preferências individuais | Pendente |
| Ocultar comentários e fotos de perfil | Preferências individuais | Pendente |
| Ocultar Mix e rádios automáticas | Preferência individual | Pendente |
| Ocultar produtos, ingressos e ofertas | Preferência individual | Pendente |
| Ocultar informações, botões, canal e inscrição | Preferências individuais | Pendente |
| Ocultar descrição, cabeçalho e sino | Preferências individuais | Pendente |
| Ocultar prateleiras de Shorts por contexto | Página inicial, pesquisa, canais e recomendações | Pendente |
| Ocultar sugestões automáticas de pesquisa | Preferência individual | Pendente |
| Ocultar miniplayer e filtros de feeds | Preferências individuais | Pendente |
| Ocultar espaços publicitários identificáveis | Ocultação visual limitada; não prometer bloqueio de rede | Pendente |
| Ocultar publicações textuais da comunidade | Preservar posts com mídia/enquetes e documentar falsos positivos | Pendente |
| Suporte desktop e móvel do YouTube | Adaptar seletores às versões reais do site | Pendente |
| Navegação SPA | Reaplicar regras sem loops de MutationObserver | Pendente |

## 5. Ferramentas de estudo e organização

| Recurso Android | Requisito desktop | Estado |
|---|---|---|
| Biblioteca/fila de vídeos | Salvar, listar, remover e abrir vídeos localmente | Pendente |
| Marcar momentos | Salvar timestamp por vídeo | Pendente |
| Anotações por vídeo | Salvar texto e timestamp associados ao vídeo | Pendente |
| Temporizador de sessão | Pausar mídia ao fim do período configurado | Pendente |
| Velocidade por canal | Memorizar velocidade por canal com limites e fallback | Pendente |
| Modo estudo | Reunir marcações e anotações | Pendente |
| Painel flutuante contextual | Mostrar somente quando a ferramenta estiver ativa | Pendente |
| Limites de dados | Impedir crescimento indefinido de listas e anotações | Pendente |

## 6. Atenção, sessões e recompensas

| Componente Android | Requisito desktop | Estado |
|---|---|---|
| Attention / AttentionActivity | Recriar fluxo e interface de atenção | Pendente |
| AttentionLogic | Separar regras de negócio da interface | Pendente |
| AttentionRewards | Preservar sistema de recompensas e persistência | Pendente |
| Sessões e controles de atenção | Inventariar gatilhos, estados e critérios diretamente no código | Pendente |

## 7. Mídia e reprodução

| Recurso Android | Requisito desktop | Estado |
|---|---|---|
| Velocidade global de vídeo | 0,5×, 0,75×, 1×, 1,25×, 1,5×, 1,75×, 2× e 2,5× quando suportado | Pendente |
| Controle de HTMLMediaElement | Aplicar playbackRate/defaultPlaybackRate e lidar com mídia dinâmica | Pendente |
| Preferência persistente de velocidade | Salvar e restaurar configuração | Pendente |
| Reprodução em segundo plano | Avaliar suporte real no Linux e no motor | Em avaliação |
| BackgroundAudioService | Substituir por integração desktop sob demanda, quando necessário | Em avaliação |
| Media3/ExoPlayer | Definir equivalência para mídias fora do player da página | Em avaliação |
| Player de mídia próprio | Inventariar fontes e catálogo de mídia | Pendente |
| Histórico de reprodução | Persistir e consultar histórico conforme política original | Pendente |
| Player em janela/PiP | Avaliar suporte do motor e do compositor | Em avaliação |
| Parar toda mídia | Controle global para abas e player próprio | Pendente |
| DRM, iframes e players proprietários | Documentar limitações; não prometer controle universal | Em avaliação |

## 8. Tradução de páginas

| Recurso Android | Requisito desktop | Estado |
|---|---|---|
| Ação Traduzir página | Ação manual no menu | Pendente |
| Identificação automática de idioma | Detectar idioma predominante sem confiar cegamente no atributo lang | Pendente |
| Tradução para português | Preservar destino inicial em português | Pendente |
| Modelos locais/offline | Selecionar mecanismo desktop e baixar sob demanda | Em avaliação |
| Cache LRU | Cache por idioma de origem/destino e texto original | Pendente |
| Processamento em lotes | Evitar bloquear interface em páginas grandes | Pendente |
| Cancelamento | Cancelar tradução em andamento | Pendente |
| Restaurar texto original | Restaurar nós alterados sem perder conteúdo original | Pendente |
| Exclusões | Excluir formulários, código, SVG, MathML e translate=no | Pendente |
| Privacidade | Não enviar texto da página a serviço remoto sem consentimento | Pendente |
| Limitações | Documentar canvas, imagens, PDFs, frames e conteúdo dinâmico | Pendente |

## 9. Diagnóstico e qualidade

| Área | Critério | Estado |
|---|---|---|
| Logs | Não registrar senhas, cookies, tokens, e-mails ou URLs sensíveis | Pendente |
| Testes de regressão | Cobrir abas, bloqueios, tradução, mídia e extensões | Pendente |
| Compatibilidade web | Testar sites de referência no motor selecionado | Pendente |
| Desempenho | Medir RAM/CPU em cenários repetíveis no N3060/4 GB | Pendente |
| Instalação | Instalação limpa no Linux Mint 64 bits | Pendente |
| Atualização | Atualizar sem perder dados locais | Pendente |
| Migração de dados | Importar dados Android exportáveis com validação e backup | Em avaliação |
| Acessibilidade | Navegação por teclado, foco, contraste e rótulos | Pendente |

## 10. Regras para atualizar a matriz

1. Não marcar recurso como concluído apenas porque existe uma tela ou botão.
2. Registrar limitações e diferenças de comportamento.
3. Vincular cada conclusão a testes reproduzíveis.
4. Manter recursos não suportados visíveis, com justificativa técnica.
5. A matriz só representa paridade real depois de testes no aplicativo desktop executando no Linux Mint.
