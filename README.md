# Navegador Maluco — Linux Mint

Aplicativo desktop próprio para Linux, com interface GTK e motor WebKitGTK. O objetivo é portar o navegador Android completo; esta primeira versão instalável entrega o núcleo de navegação desktop e uma parte inicial dos recursos.

**Projeto Android de referência:** [MaluquinhoDev/NavegadorMaluco](https://github.com/MaluquinhoDev/NavegadorMaluco)

## Baixar e instalar

A cada atualização aprovada pelo GitHub Actions, o pacote Debian `.deb` é publicado como artefato da execução.

1. Abra [GitHub Actions](https://github.com/MaluquinhoDev/NAvegadorMAlucoParaCOmputadorLinux/actions).
2. Entre na execução mais recente com resultado verde.
3. Na seção Artifacts, baixe `navegador-maluco-linux-mint-deb`.
4. Extraia o ZIP.
5. No terminal, entre na pasta extraída e execute:

```bash
sudo apt install ./navegador-maluco_0.4.4_all.deb
```

O gerenciador de pacotes instala as dependências GTK/WebKitGTK. Depois, abra **Navegador Maluco** pelo menu de aplicativos ou execute:

```bash
navegador-maluco
```

Para instalar a compilação nativa Nuitka, baixe também o artefato `navegador-maluco-native-deb-ubuntu-24.04-amd64`, extraia o ZIP e execute:

```bash
sudo apt install ./navegador-maluco-native_0.4.4_amd64.deb
navegador-maluco-native
```

As duas versões têm comandos e entradas de menu separados e podem coexistir. A versão nativa foi construída em Ubuntu 24.04 amd64 e está direcionada inicialmente ao Linux Mint 22.x.

O pacote foi configurado para sistemas Debian/Ubuntu 64 bits, incluindo Linux Mint. A disponibilidade do pacote WebKitGTK depende da versão do Mint; o pacote declara WebKitGTK 4.1 ou 4.0.

## Otimizações para computadores com pouca memória

A versão 0.4.4 adota um perfil econômico adaptativo para máquinas com aproximadamente 4 GB de RAM:

- Limite de 12 abas abertas.
- Sugestões locais na barra de endereço, combinando histórico, favoritos e abas abertas sem enviar os termos digitados a um serviço externo.
- Mecanismo de pesquisa selecionável: DuckDuckGo, Startpage ou Google.
- Indicador estimado de carregamento, botão para interromper navegação e estados de conexão, redirecionamento e recebimento de conteúdo.
- Diagnóstico de carregamento por navegação: tempo total observado e métricas disponíveis de DNS, conexão, TLS, TTFB, DOM e recursos, sem armazenar URLs ou conteúdo.
- Localizar texto na página (Ctrl+F) e zoom (Ctrl++, Ctrl+- e Ctrl+0).
- Pré-carregamento especulativo não é ativado: em 4 GB de RAM, o ganho potencial não justifica o consumo contínuo de memória e rede.
- Até 3 WebViews residentes como alvo.
- Estacionamento automático de abas inativas após 3 minutos, quando o motor confirma que não há mídia tocando, campo de formulário focado ou alterações de formulário detectadas.
- Abas estacionadas mantêm URL e título; ao restaurar, a página é carregada novamente. Estado transitório de aplicações web pode não ser preservado.
- Abas com reprodução ativa ou formulários alterados não são estacionadas automaticamente.
- A aceleração gráfica permanece na política padrão sob demanda do WebKitGTK; não é forçada nem desativada.
- Diagnóstico do sistema disponível em scripts/diagnose-performance.sh. Guia completo: [docs/PERFORMANCE_LOW_MEMORY.md](docs/PERFORMANCE_LOW_MEMORY.md).
- Gravações do histórico agrupadas em lotes, com poda periódica em vez de apagar registros antigos a cada navegação.
- Sugestões da barra de endereço com debounce de 180 ms para evitar consultas ao banco a cada tecla.
- Ajuste adaptativo da meta de WebViews usando MemAvailable e PSI do Linux: normal (3), pressão alta (2) e crítica (1), sem forçar encerramentos de páginas ativas.
- Scripts de velocidade de mídia sem MutationObserver global; velocidade 1× não instala observadores e velocidades personalizadas usam eventos delegados.
- Diagnóstico inclui PSI de CPU/memória/I/O e PSS quando o kernel disponibiliza smaps_rollup.

O estacionamento é conservador: a meta de três WebViews residentes pode ser temporariamente excedida quando as abas restantes estão ocupadas ou não podem ser estacionadas com segurança.

## Pesquisa comparativa de navegadores Linux

| Navegador | Abordagem observada | Decisão aplicada ao Navegador Maluco |
|---|---|---|
| Firefox | Barra inteligente que reúne histórico, favoritos, abas abertas e sugestões de pesquisa; descarregamento de abas sob pressão de memória. | Adotadas sugestões locais e gestão conservadora de abas residentes. |
| Chromium | Pré-renderização de páginas prováveis para navegação quase instantânea, com custo adicional de memória e rede. | Não ativada por padrão: o custo especulativo é inadequado ao perfil de 4 GB. |
| GNOME Web | Navegador GTK baseado em WebKitGTK, próximo da arquitetura usada neste projeto. | Referência de integração GTK/WebKitGTK, sem trocar o motor. |
| Falkon | Navegador gráfico baseado em Chromium, listado entre as opções Linux. | Referência de navegador leve, mas sem copiar recursos que aumentem dependências ou consumo. |
| qutebrowser | Navegação orientada ao teclado. | Atalhos de localizar e zoom foram incorporados; o restante do modelo modal não foi adotado. |

A implementação atual combina sugestões privadas locais, seleção de mecanismo de pesquisa, progresso de carregamento, interrupção de navegação, localizar na página e controle de zoom. O indicador usa a estimativa fornecida pelo WebKitGTK; não representa uma medição exata do tempo restante.

Fontes técnicas:
- [Mozilla — arquitetura da barra de endereço](https://firefox-source-docs.mozilla.org/browser/urlbar/index.html)
- [Mozilla — descarregamento de abas sob pressão de memória](https://gecko-docs.mozilla.org/browser/components/tabbrowser/docs/tab-unloading.html)
- [Chrome — pré-renderização e seus custos](https://developer.chrome.com/docs/web-platform/prerender-pages)
- [WebKitGTK — progresso estimado de carregamento](https://webkitgtk.org/reference/webkit2gtk/stable/class.WebView.html)
- [WebKitGTK — localizar texto na página](https://webkitgtk.org/reference/webkit2gtk/stable/class.FindController.html)
- [Debian — catálogo de navegadores Linux](https://wiki.debian.org/WebBrowsers)

## O que já funciona nesta versão

- Aplicativo Linux com janela própria.
- Motor WebKitGTK integrado, sem exigir Firefox como hospedeiro.
- Barra de endereço, pesquisa com DuckDuckGo/Startpage/Google e sugestões locais.
- Abas múltiplas, com limite de 12.
- Voltar, avançar, recarregar e página inicial.
- Favoritos e histórico local em SQLite.
- Downloads na pasta `~/Downloads`.
- Controle de velocidade de mídia HTML5: 0,5× a 2,5×.
- YouTube Focus: script original do Android reaproveitado, preferências iniciais e painel nativo de opções.
- Bloqueio de navegação direta para URLs de Shorts.
- Dados e configurações armazenados localmente no perfil do usuário.

## Limitações conhecidas

Esta é uma **versão inicial do shell desktop**, não a paridade integral com o Android. Ainda faltam, entre outros recursos, constelações e gestão avançada de sessões, perfis isolados, gerenciador completo de extensões, bloqueador de rede, tradução offline, player próprio/Media3, PiP, migração dos dados Android e várias opções avançadas de atenção. O YouTube pode alterar seu DOM e quebrar seletores.

O WebKitGTK não é Chromium nem Gecko. Alguns sites, codecs, DRM, autenticação e extensões podem se comportar de forma diferente. Não há medição publicada de consumo no Celeron N3060 ainda; o hardware de referência continua sendo Celeron N3060 com 4 GB de RAM.

## Desenvolvimento local

Dependências no Linux Mint:

```bash
sudo apt update
sudo apt install python3 python3-gi gir1.2-gtk-3.0 gir1.2-webkit2-4.1
```

Em versões que não oferecem WebKitGTK 4.1, instale `gir1.2-webkit2-4.0`.

Executar a partir do repositório:

```bash
python3 app/navegador_maluco.py
```

Testes e pacote:

```bash
python3 -m unittest discover -s tests -v
APP_VERSION=0.4.4 bash scripts/build-deb.sh
```

## Versões Python e nativa

A CI publica dois pacotes separados:
- **Python:** `navegador-maluco-linux-mint-deb`, arquitetura independente, usa o interpretador do sistema.
- **Nativa Nuitka:** `navegador-maluco-native-deb-ubuntu-24.04-amd64`, executável compilado, empacotado como .deb para amd64 e validado em Ubuntu 24.04. O comando instalado é `navegador-maluco-native`.

A versão nativa acelerada ainda depende do runtime Python e das bibliotecas GTK/WebKitGTK compatíveis. O pacote construído em Ubuntu 24.04 destina-se inicialmente à base Ubuntu 24.04 (Linux Mint 22.x); não deve ser instalado em Mint 21.x ou Debian antigo sem build e teste específicos. A CI instala as duas variantes, executa smoke tests e compara cinco inicializações Python versus Nuitka em ambiente idêntico, medindo tempo e pico de RSS. Esse benchmark é do runner Ubuntu, não do Celeron físico nem da navegação completa.

Detalhes e critérios de promoção: [docs/NATIVE_BUILD.md](docs/NATIVE_BUILD.md).

## Arquitetura e inventário

- [Plano de migração integral](docs/PORTING_PLAN.md)
- [Arquitetura desktop](docs/ARCHITECTURE.md)
- [Matriz de paridade Android/Linux](docs/FEATURE_PARITY.md)

## Estrutura

- `app/`: aplicação GTK/WebKitGTK e lógica do navegador.
- `app/assets/youtube-focus.js`: content script reaproveitado do Android.
- `packaging/`: ícone e entrada de menu do Linux.
- `scripts/build-deb.sh`: construção do pacote instalável.
- `scripts/install-linux-mint.sh`: instalação local a partir de um clone que já contenha o .deb em `dist/`.
- `tests/`: testes unitários da lógica independente da interface.
- `.github/workflows/linux-ci.yml`: testes e construção automática do .deb.

## Privacidade

Histórico, favoritos e preferências ficam no computador. A aplicação não implementa telemetria própria. O motor WebKitGTK mantém as conexões necessárias para carregar os sites visitados. O YouTube Focus manipula a interface do YouTube; não altera o algoritmo da plataforma nem garante bloqueio de anúncios dentro do player.
