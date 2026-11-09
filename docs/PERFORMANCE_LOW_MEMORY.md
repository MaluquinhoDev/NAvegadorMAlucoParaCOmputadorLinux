# Perfil econômico: Intel Celeron N3060 e 4 GB de RAM

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

Execute bash scripts/diagnose-performance.sh antes e durante o uso. Compare o mesmo conjunto de páginas, mesmo nível de zoom, mesma qualidade de vídeo e duração. Registre:
- RAM disponível e swap usada;
- RSS do processo principal e processos WebKit;
- CPU após 1 minuto de estabilização;
- tempo para abrir/retomar uma aba;
- comportamento ao alternar entre 4–6 páginas;
- uso de CPU durante vídeo 480p/720p.

A CI confirma sintaxe, testes e empacotamento, mas não mede desempenho físico no Celeron N3060. Resultados reais exigem medição no computador-alvo.
