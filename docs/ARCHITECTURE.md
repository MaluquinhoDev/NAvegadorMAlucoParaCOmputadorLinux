# Arquitetura desktop

## Visão geral

```text
Firefox (motor e interface do navegador)
└── Navegador Maluco — extensão WebExtension
    ├── content scripts por domínio
    │   └── YouTube Focus
    ├── browser.storage.local
    │   └── preferências e dados locais
    ├── página de opções (fase seguinte)
    └── APIs WebExtensions
        └── bloqueios e integração com o navegador
```

## Princípio central

O Firefox é o motor de navegação. O projeto não inicia Chromium, GeckoView ou WebKit em paralelo. Isso reduz duplicação de processos e mantém o escopo adequado a um Celeron N3060 com 4 GB de RAM.

## Reaproveitamento do Android

| Componente Android | Destino desktop |
|---|---|
| Content scripts JavaScript | Reaproveitar e adaptar |
| Preferências da extensão | `browser.storage.local` |
| Android WebView / GeckoView | Firefox hospedeiro; não portar |
| SharedPreferences | armazenamento WebExtension |
| AndroidX Media3 | APIs HTML5 e APIs do navegador, quando disponíveis |
| Google ML Kit Android | avaliar alternativa desktop separadamente |
| Serviços Android em segundo plano | não migrar sem necessidade comprovada |
| UI Kotlin/Activities | interface WebExtension em HTML/CSS/JS |

## Estrutura atual

- `extension/youtube-focus/manifest.json`: metadados e permissões da extensão.
- `extension/youtube-focus/content.js`: lógica de foco adaptada do projeto Android.
- `docs/`: decisões, plano e limites.
- `scripts/`: verificações reproduzíveis.
- `.github/workflows/`: CI e artefato ZIP.

## Compatibilidade e segurança

- A extensão declara apenas os domínios necessários para o content script inicial.
- O armazenamento é local.
- O código da extensão não injeta bibliotecas remotas.
- O script deve tolerar elementos ausentes e alterações no DOM do YouTube.
- Os seletores CSS são específicos do YouTube e podem ficar obsoletos.
- Não usar permissões amplas sem uma função concreta que as exija.
- Não tratar ocultação visual como bloqueio de rede: são mecanismos diferentes.

## Desempenho

A primeira versão não deve criar timers de alta frequência nem manter observers fora das páginas correspondentes. O content script atual observa mudanças do DOM para acompanhar a navegação SPA; a medição deve verificar o custo real em páginas longas e feeds dinâmicos.

A métrica correta é a diferença entre Firefox sem extensão e Firefox com extensão no mesmo conjunto de páginas, com número de abas e condições comparáveis.
