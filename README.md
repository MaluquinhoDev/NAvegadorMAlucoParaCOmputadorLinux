# Navegador Maluco — Linux

Portabilidade **integral** do aplicativo Android [NavegadorMaluco](https://github.com/MaluquinhoDev/NavegadorMaluco) para um navegador desktop no Linux Mint.

> **Escopo:** recriar o navegador completo, preservando sua identidade, interface e conjunto de recursos. A extensão Firefox existente é apenas um protótipo técnico de reaproveitamento de uma funcionalidade; não representa o produto final.

## Objetivo do projeto

Construir um aplicativo de navegação próprio para Linux, com janela e interface próprias, gerenciamento de abas e sessões, ferramentas de estudo, bloqueios, extensões, reprodução de mídia e tradução de páginas. O Firefox instalado no sistema não será a interface final nem um requisito para usar o Navegador Maluco.

O projeto deve manter paridade funcional com o aplicativo Android sempre que houver equivalente tecnicamente viável no desktop. Recursos dependentes de APIs Android serão reimplementados com APIs Linux/WebKit ou substitutos documentados, e não simplesmente removidos.

## Hardware de referência

- Linux Mint 64 bits.
- Intel Celeron N3060, 2 núcleos.
- 4 GB de RAM.

O consumo de memória, CPU e armazenamento é requisito arquitetural. O navegador deve evitar processos e serviços residentes desnecessários, limitar abas residentes e permitir descarregar/estacionar abas inativas.

## Arquitetura-alvo em avaliação

A direção arquitetural passa a ser um aplicativo desktop próprio baseado em **Tauri + WebKitGTK**, sujeito a uma prova de conceito de desempenho e compatibilidade no Linux Mint. Essa opção permite janela, menus, armazenamento e integração nativos sem embutir uma distribuição Chromium como o Electron.

A arquitetura não está declarada como validada: WebKitGTK possui diferenças de compatibilidade em relação ao Android WebView/Chromium e ao GeckoView. O motor, a versão mínima do Linux Mint e o empacotamento só serão fixados após testes reproduzíveis. A extensão Firefox deste repositório permanece como laboratório de reaproveitamento de JavaScript, não como destino final.

## Funcionalidades a portar

O inventário inicial está em [docs/FEATURE_PARITY.md](docs/FEATURE_PARITY.md). Inclui, entre outros:

- Navegação, barra de endereço/pesquisa, histórico, downloads e múltiplas abas.
- Abas estacionadas, fixadas e organizadas em constelações.
- Perfis e isolamento de dados de navegação, dentro dos limites do motor escolhido.
- Gerenciador de extensões locais e API compatível com o formato já usado pelo projeto.
- Bloqueadores e controles de privacidade.
- YouTube sem distrações, incluindo preferências detalhadas e ferramentas de estudo.
- Biblioteca/fila de vídeos, marcações de tempo, anotações e temporizador.
- Velocidade de reprodução, controles de mídia e modos de reprodução em janela.
- Tradução de páginas com identificação de idioma, cache e restauração do texto original.
- Ferramentas de atenção, sessão e recompensas.
- Diagnóstico de compatibilidade de login/cookies sem registrar credenciais ou tokens.

O inventário é baseado no código e na documentação disponíveis no repositório Android de origem. Cada item deve receber estado de implementação e teste; não se considera concluído apenas por existir uma tela.

## Estado real deste repositório

- [x] Diagnóstico inicial do projeto Android.
- [x] Protótipo de extensão Firefox para testar o reaproveitamento de um content script.
- [x] Validação estática e empacotamento da extensão no GitHub Actions.
- [x] Escopo corrigido para migração integral do navegador.
- [ ] Prova de conceito do aplicativo desktop próprio.
- [ ] Migração da interface e do núcleo de navegação.
- [ ] Paridade funcional com o aplicativo Android.
- [ ] Testes de instalação, estabilidade, compatibilidade e desempenho no Linux Mint.

**Não existe ainda um navegador desktop completo neste repositório.** A CI da extensão comprova apenas validação estática e empacotamento daquele protótipo; não comprova a execução do navegador completo.

## Estrutura

- `extension/youtube-focus/`: protótipo isolado de extensão Firefox.
- `docs/FEATURE_PARITY.md`: inventário de recursos Android e matriz de paridade desktop.
- `docs/PORTING_PLAN.md`: plano de migração integral.
- `docs/ARCHITECTURE.md`: arquitetura desktop e decisões técnicas.
- `scripts/` e `.github/workflows/`: validação do protótipo de extensão.

## Princípios de migração

1. Não reduzir o projeto a uma extensão.
2. Não remover funcionalidades silenciosamente: registrar equivalências, limitações e decisões.
3. Separar lógica de negócio de APIs específicas do Android.
4. Preservar dados e preferências sempre que houver formato de migração seguro.
5. Priorizar processamento local e privacidade por padrão.
6. Medir desempenho no hardware de referência; não inventar metas ou resultados.
7. Manter testes de regressão para cada recurso migrado.

## Projeto original

[MaluquinhoDev/NavegadorMaluco](https://github.com/MaluquinhoDev/NavegadorMaluco)
