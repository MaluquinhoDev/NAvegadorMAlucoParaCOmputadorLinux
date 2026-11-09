# Perfil econômico: Intel Celeron N3060 e 4 GB de RAM

## Diagnóstico por recurso da versão 0.4.2

- A WebView acompanha os eventos `resource-load-started`, `sent-request`, `received-response`, `finished` e `failed` do WebKitGTK.
- O tooltip da navegação apresenta contagens de recursos iniciados/concluídos/falhos, respostas HTTP com status 400 ou superior, redirecionamentos, bytes declarados nas respostas e durações média/máxima observadas.
- O diagnóstico mantém apenas contadores e tempos em memória durante a navegação. Não armazena URLs, parâmetros de pesquisa, cabeçalhos, cookies nem conteúdo das páginas.
- Os bytes declarados por respostas podem não representar o tráfego efetivo (compressão, cache, respostas parciais e respostas sem tamanho conhecido). Recursos que falham antes de uma resposta não contribuem para bytes. Os valores servem para localizar padrões, não para substituir um waterfall de rede ou um benchmark.
- A instrumentação mede e diagnostica; não acelera por si só o carregamento. Ainda não há benchmark comparativo executado no Celeron N3060.

## Otimizações adicionais da versão 0.4.1

- **Inicialização em duas etapas:** a janela apresenta primeiro uma tela local mínima; a navegação para a página inicial remota é adiada em 400 ms após a janela ser mostrada. Isso melhora a responsividade percebida da interface, mas não reduz o tempo de resposta do site nem garante menor tempo total de inicialização.
- **Tempo de navegação observado:** a barra de status informa o intervalo entre `LoadEvent.STARTED` e `LoadEvent.FINISHED`. O tooltip apresenta os tempos que a Navigation Timing API disponibiliza para DNS, conexão, TLS, TTFB e DOM, além da quantidade e dos bytes transferidos dos recursos observáveis. O navegador não grava URLs nem conteúdo. Recursos de outras origens podem ocultar parte das métricas sem `Timing-Allow-Origin`; valores zero não provam latência zero.

## Otimizações adicionais da versão 0.4.0

- **PSI + MemAvailable:** o navegador consulta `/proc/pressure/memory` e `MemAvailable` a cada ciclo de gestão de abas. Em estado normal, mantém a meta de 3 WebViews e 180 s de inatividade. Com pressão alta sustentada (menos de 512 MiB disponíveis e PSI `some avg10` ≥ 2%), reduz a meta para 2 e a inatividade para 120 s. Em pressão crítica (menos de 384 MiB disponíveis e PSI `full avg10` ≥ 1%), reduz a meta para 1 e a inatividade para 90 s. Se PSI não estiver disponível ou os dados forem inválidos, mantém o perfil normal.
- **Histórico em lotes:** páginas concluídas entram em uma fila e são persistidas em transação agrupada a cada 3 segundos; a poda do histórico ocorre em blocos de 100 novas entradas. Visitas repetidas ao mesmo URL em 30 segundos atualizam o registro recente. O lote é descarregado ao fechar a janela.
- **SQLite:** WAL já era usado; agora há `busy_timeout` de 500 ms, cache de página de 2 MiB e armazenamento temporário em memória. A durabilidade padrão do SQLite é preservada; não foi usado `synchronous=OFF`.
- **Autocomplete:** as consultas aguardam 180 ms após a última tecla, evitando uma consulta síncrona por caractere.
- **Mídia:** em 1× nenhum listener de mídia é registrado; o script retorna imediatamente. Em outras velocidades, dois eventos delegados tratam mídias atuais e dinâmicas; não há varredura contínua de mutações do DOM.
- **Script YouTube:** arquivo carregado uma vez na inicialização, em vez de relido do disco a cada navegação.
- **Configurações:** gravação por arquivo temporário + rename, evitando deixar JSON truncado se o processo for interrompido durante a escrita.


## Otimizações implementadas no aplicativo

- Limite de 12 abas abertas.
- Alvo de três WebViews residentes.
- Verificação periódica de abas inativas.
- Estacionamento após 180 segundos sem uso, apenas quando a página informa que não há mídia tocando, campo de formulário focado ou alterações em formulários detectadas.
- Restauração sob demanda pela seleção da aba ou pelo botão no placeholder.
- Mantém o padrão de aceleração gráfica do WebKitGTK (sob demanda).

### Limites conhecidos do estacionamento

Estacionar destrói a WebView e preserva URL/título, não a árvore DOM. Ao restaurar, o site carrega novamente. Estado transitório de aplicações SPA, formulários sem eventos detectáveis, uploads, páginas autenticadas com sessão volátil ou conteúdo não salvo podem se perder. Por isso a suspensão automática é conservadora e não ocorre enquanto a página está carregando, reproduzindo mídia ou apresenta formulário alterado detectado. A contagem de WebViews pode superar três quando não há candidata segura.

## Ajustes de sistema: o que vale a pena

1. **ZRAM:** em máquinas com 4 GB, swap comprimida em RAM pode evitar encerramentos por falta de memória e reduzir acessos ao disco. Ela consome CPU para comprimir/descomprimir; o ganho depende do padrão de uso. Verifique primeiro com zramctl e swapon --show. Não configure duas soluções ZRAM simultaneamente.
2. **Swap em SSD/HD:** mantenha uma área de swap como rede de segurança. Swap em disco é muito mais lenta que RAM e não transforma 4 GB em memória rápida.
3. **Aceleração VA-API:** verifique com vainfo. A presença de Quick Sync no anúncio do processador não garante que o driver, codec, WebKitGTK e pipeline de vídeo estejam integrados. Não instale drivers aleatórios nem force flags experimentais.
4. **Drivers gráficos:** mantenha os pacotes recomendados pelo Linux Mint/Ubuntu e atualizações de segurança. Forçar renderização por software pode aumentar bastante o uso de CPU.
5. **Serviços em segundo plano:** desative somente serviços que o usuário reconheça e não utiliza. Não há ganho garantido ao remover serviços essenciais do Mint.
6. **Navegação:** limite abas pesadas, evite vários vídeos simultâneos e feche páginas de aplicações web que não estejam em uso.
7. **Temperatura e energia:** use o equipamento em superfície ventilada e observe throttling. O N3060 tem envelope térmico baixo; calor pode reduzir frequência sustentada.
8. **Resolução e efeitos do desktop:** reduzir animações e efeitos do compositor pode ajudar a GPU integrada e a memória compartilhada, com impacto visual.
9. **Conteúdo e extensões:** cada extensão, script injetado, feed infinito e aplicação JavaScript pode aumentar CPU/RAM. O YouTube Focus já usa MutationObserver e deve permanecer restrito ao YouTube.

## O que não foi aplicado deliberadamente

- Não forçar aceleração GPU sempre ligada nem desligá-la globalmente: o padrão WebKitGTK é sob demanda e o resultado depende dos drivers.
- Não desativar JavaScript, imagens, WebGL, áudio ou armazenamento web: isso quebraria sites e autenticação.
- Não limpar cache/cookies automaticamente: pode apagar sessões e causar mais downloads e CPU.
- Não elevar swappiness ou alterar sysctl sem medição.
- Não instalar serviços de otimização residentes.
- Não prometer reprodução 1080p ou decodificação por hardware sem confirmar VA-API no equipamento.

## Medição reproduzível

Execute `bash scripts/diagnose-performance.sh` antes e durante o uso. O diagnóstico agora registra PSI de CPU, memória e I/O, MemAvailable e RSS/PSS dos processos do navegador quando `smaps_rollup` está disponível. Compare o mesmo conjunto de páginas, mesmo nível de zoom, mesma qualidade de vídeo e duração. Registre:
- RAM disponível e swap usada;
- RSS do processo principal e processos WebKit;
- CPU após 1 minuto de estabilização;
- tempo para abrir/retomar uma aba;
- comportamento ao alternar entre 4–6 páginas;
- uso de CPU durante vídeo 480p/720p.

A CI confirma sintaxe, testes e empacotamento, mas não mede desempenho físico no Celeron N3060. Os limites adaptativos são heurísticas conservadoras, não um benchmark nem uma promessa de redução fixa de RAM. Resultados reais exigem medição no computador-alvo.

## Referências técnicas

- [Linux PSI — documentação do systemd](https://systemd.io/PRESSURE/): significado de pressão de CPU, memória e I/O.
- [SQLite WAL](https://www.sqlite.org/wal.html): concorrência, checkpoints, transações e compromissos do modo WAL.
- [SQLite PRAGMA](https://www.sqlite.org/pragma.html): busy_timeout, cache e comportamento de sincronização.
- [GLib Main Loop](https://docs.gtk.org/glib/main-loop.html): timers, callbacks e ciclo de eventos da interface.
- [WebKitGTK MemoryPressureSettings](https://github.com/WebKit/WebKit/blob/main/Source/WebKit/UIProcess/API/glib/WebKitMemoryPressureSettings.cpp): advertência contra limites de memória agressivos.
- [WebKitGTK 2.54.2](https://www.webkitgtk.org/2026/10/23/webkitgtk2.54.2-released.html): melhorias na liberação de páginas suspensas e processos ociosos sob pressão de memória.
