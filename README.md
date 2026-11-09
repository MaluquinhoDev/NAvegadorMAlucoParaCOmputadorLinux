# Navegador Maluco — Linux

Portabilidade do projeto [NavegadorMaluco](https://github.com/MaluquinhoDev/NavegadorMaluco) para computadores Linux, com prioridade para Linux Mint e hardware de baixo consumo.

> **Estado atual:** planejamento técnico e primeira base da extensão Firefox. Isto ainda não é um navegador independente nem uma migração completa do aplicativo Android.

## Objetivo

Levar os recursos mais úteis do Navegador Maluco para o desktop sem obrigar um computador modesto a executar outro navegador completo em paralelo.

A primeira plataforma-alvo é **Firefox no Linux Mint**. O Firefox fornece o motor de navegação; o projeto fornece a camada de foco e personalização.

## Hardware de referência

- Intel Celeron N3060 (2 núcleos / 2 threads, baixo consumo)
- 4 GB de RAM
- Linux Mint 64 bits

As decisões iniciais priorizam poucos processos, baixo consumo de memória, ausência de serviços residentes e processamento local.

## O que existe neste repositório

- `extension/youtube-focus/`: primeira adaptação da extensão YouTube sem distrações.
- `docs/PORTING_PLAN.md`: plano de migração por etapas.
- `docs/ARCHITECTURE.md`: arquitetura desktop e limites da migração.
- `scripts/check-extension.sh`: validação estática local.
- `.github/workflows/linux-ci.yml`: validação e empacotamento automático no GitHub Actions.

## Instalação de desenvolvimento

1. Abra `about:debugging` no Firefox.
2. Selecione **Este Firefox**.
3. Clique em **Carregar extensão temporária**.
4. Selecione `extension/youtube-focus/manifest.json`.

A extensão temporária permanece instalada até o Firefox ser reiniciado. O pacote ZIP é produzido pelo GitHub Actions como artefato de CI; ainda não é uma extensão assinada/publicada no AMO.

## Verificação local

Requisitos: Bash, Node.js e `zip`.

```bash
bash scripts/check-extension.sh
```

## Limites conhecidos

- O motor Android WebView/GeckoView não pode ser reutilizado diretamente como aplicativo Linux.
- A extensão atual é um primeiro recorte funcional: YouTube sem distrações.
- A interface de configurações, bloqueio de outros domínios, biblioteca sincronizada e tradução de páginas ainda não foram migrados.
- A compatibilidade dos seletores do YouTube precisa de testes contínuos, pois a interface do site muda com frequência.
- Não há promessa de desempenho absoluto: o consumo total também depende das abas, vídeos e extensões abertas no Firefox.

## Projeto de origem

O aplicativo Android original permanece separado: [MaluquinhoDev/NavegadorMaluco](https://github.com/MaluquinhoDev/NavegadorMaluco).
