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
sudo apt install ./navegador-maluco_0.2.0_all.deb
```

O gerenciador de pacotes instala as dependências GTK/WebKitGTK. Depois, abra **Navegador Maluco** pelo menu de aplicativos ou execute:

```bash
navegador-maluco
```

O pacote foi configurado para sistemas Debian/Ubuntu 64 bits, incluindo Linux Mint. A disponibilidade do pacote WebKitGTK depende da versão do Mint; o pacote declara WebKitGTK 4.1 ou 4.0.

## Otimizações para computadores com pouca memória

A versão 0.2.0 adota um perfil econômico para máquinas com aproximadamente 4 GB de RAM:

- Limite de 12 abas abertas.
- Até 3 WebViews residentes como alvo.
- Estacionamento automático de abas inativas após 3 minutos, quando o motor confirma que não há mídia tocando, campo de formulário focado ou alterações de formulário detectadas.
- Abas estacionadas mantêm URL e título; ao restaurar, a página é carregada novamente. Estado transitório de aplicações web pode não ser preservado.
- Abas com reprodução ativa ou formulários alterados não são estacionadas automaticamente.
- A aceleração gráfica permanece na política padrão sob demanda do WebKitGTK; não é forçada nem desativada.
- Diagnóstico do sistema disponível em scripts/diagnose-performance.sh. Guia completo: [docs/PERFORMANCE_LOW_MEMORY.md](docs/PERFORMANCE_LOW_MEMORY.md).

O estacionamento é conservador: a meta de três WebViews residentes pode ser temporariamente excedida quando as abas restantes estão ocupadas ou não podem ser estacionadas com segurança.

## O que já funciona nesta versão

- Aplicativo Linux com janela própria.
- Motor WebKitGTK integrado, sem exigir Firefox como hospedeiro.
- Barra de endereço e pesquisa DuckDuckGo.
- Abas múltiplas, com limite de 30.
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
APP_VERSION=0.1.0 bash scripts/build-deb.sh
```

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
