# Arquitetura do Navegador Maluco para Linux

## 1. Visão do produto

O destino é um navegador desktop completo e independente, com janela própria. O Firefox não é o hospedeiro da aplicação final. A extensão Firefox existente é um protótipo auxiliar para validar o reaproveitamento de JavaScript.

## 2. Arquitetura proposta

Direção inicial: Tauri + WebKitGTK, pendente de prova de conceito no Linux Mint de referência.

```text
Navegador Maluco (aplicativo Linux)
├── Shell desktop (Tauri)
│   ├── janela, menus, atalhos e diálogos
│   └── comandos nativos restritos
├── Interface do navegador
│   ├── barra de endereço e pesquisa
│   ├── abas, constelações e abas estacionadas
│   ├── histórico, favoritos, downloads
│   └── configurações e ferramentas
├── Núcleo de navegação
│   ├── WebKitGTK / WebView
│   ├── política de navegação e permissões
│   ├── cookies, armazenamento e perfis
│   └── gerenciamento do ciclo de vida das abas
├── Recursos do Navegador Maluco
│   ├── extensões e content scripts
│   ├── bloqueadores e privacidade
│   ├── atenção e YouTube Focus
│   ├── ferramentas de estudo
│   ├── mídia e velocidade
│   └── tradução de páginas
└── Persistência local
    ├── preferências
    ├── histórico e favoritos
    ├── biblioteca, timestamps e anotações
    └── sessões, grupos e dados de extensão
```

## 3. Fronteiras entre camadas

- **Interface:** apresenta estado e encaminha ações; não deve conter políticas de segurança ou persistência diretamente.
- **Shell nativo:** executa somente operações explicitamente autorizadas, com validação de parâmetros.
- **Núcleo de navegação:** controla URLs, permissões, cookies, downloads, abas e eventos do motor.
- **Serviços de recursos:** atenção, tradução, mídia e extensões não devem depender diretamente de componentes visuais.
- **Persistência:** usa armazenamento versionado, migrações e limites de tamanho.

O frontend não recebe acesso irrestrito ao sistema de arquivos nem executa comandos arbitrários. A superfície de comandos Tauri deve ser mínima e validada.

## 4. Mapeamento Android → Linux

| Android | Desktop proposto | Observações |
|---|---|---|
| `MainActivity.kt` e UI Android | Shell Tauri + interface própria | Recriar layout, navegação e estados. |
| Android WebView | WebKitGTK | Compatibilidade deve ser testada; não é o mesmo motor/versão. |
| GeckoView separado | Não há equivalência direta assumida | Investigar necessidade real e estratégia separada. |
| SharedPreferences | Preferências locais versionadas | Migrar apenas dados exportáveis. |
| `filesDir` e arquivos privados | Diretório de dados do usuário | Permissões restritas e migrações. |
| Android DownloadManager | Downloads do motor + integração desktop | Validar destino, progresso e cancelamento. |
| Activity Result / seletor de arquivos | Diálogos GTK/portal | Respeitar permissões do desktop. |
| ExtensionManager | Serviço de extensões desktop | API WebExtension parcial; declarar compatibilidade real. |
| Content scripts JS/CSS | Content scripts adaptados | Reaproveitamento sujeito a diferenças de APIs e CSP. |
| AndroidX Media3 / ExoPlayer | APIs de mídia WebKit + integração Linux | Não presumir equivalência para DRM ou players externos. |
| PiP Android | PiP/janela flutuante desktop | Depende do compositor e do motor. |
| Google ML Kit Android | Motor local desktop a selecionar | Modelos, licenças e consumo devem ser avaliados. |
| Serviços Android | Serviços sob demanda / integração desktop | Evitar daemon residente sem necessidade. |

## 5. Inventário funcional

A lista detalhada e seu estado de migração estão em [FEATURE_PARITY.md](FEATURE_PARITY.md). Ela é a referência para não reduzir o escopo a YouTube Focus.

## 6. Modelo de abas e memória

O Android já distingue abas residentes e estacionadas, além de abas fixadas e constelações. O desktop deve preservar esse conceito.

Regras arquiteturais:
- Uma aba estacionada mantém metadados mínimos (URL, título, grupo, identificador e perfil), não uma WebView ativa.
- A restauração recria o contexto de navegação; não promete restaurar DOM, formulário, autenticação ou reprodução.
- Abas fixadas não devem ser estacionadas automaticamente sem política explícita.
- A troca de aba não pode criar WebViews sem limite.
- Fechamento deve liberar observers, scripts, timers e recursos associados.

## 7. Perfis, cookies e segurança

O Android aplica política de cookies de terceiros por domínio e possui diagnóstico específico de autenticação. O desktop precisa reavaliar essas regras para APIs reais do WebKitGTK.

Princípios:
- Não ativar cookies de terceiros globalmente como correção genérica.
- Não modificar cookies existentes sem ação explícita.
- Isolamento de perfil só será anunciado quando o motor realmente separar cookies, cache e armazenamento.
- Diagnóstico deve registrar categorias e contadores mínimos; nunca senhas, tokens, cookies, e-mails ou URLs completas.
- Validar esquemas e destinos antes de abrir links externos.
- Restringir comandos nativos e permissões por princípio do menor privilégio.

## 8. Extensões e scripts

O projeto Android possui manifests locais, content scripts, CSS e API JavaScript `browser` para mensagens e armazenamento. O desktop deverá definir um subconjunto compatível e versionado.

Não declarar compatibilidade integral com Firefox WebExtensions até implementar e testar cada API. A extensão YouTube Focus atual pode servir como fixture de regressão, mas sua execução no Firefox não prova que funcionará dentro do motor desktop escolhido.

## 9. Privacidade e dados

- Processamento local como padrão.
- Sem telemetria própria por padrão.
- Nenhum conteúdo de página enviado a serviço remoto sem consentimento explícito.
- Modelos de tradução e atualizações devem informar origem, tamanho e finalidade.
- Logs não devem incluir credenciais, tokens, cookies, conteúdo de formulários ou URLs com parâmetros sensíveis.
- Persistência com versão de esquema e migrações testáveis.

## 10. Desempenho e observabilidade

Métricas necessárias:
- Tempo de inicialização a frio e quente.
- RAM ociosa, com uma página, com vídeo e com múltiplas abas.
- CPU durante carregamento, scroll e reprodução.
- Memória recuperada ao estacionar e fechar abas.
- Tamanho instalado e tamanho de modelos adicionais.

Comparações devem registrar distribuição Linux, versão do motor, hardware, páginas, quantidade de abas e duração. Não há números de desempenho aprovados ainda.

## 11. CI e validação

A CI atual valida apenas a extensão Firefox experimental. A CI do aplicativo desktop deverá futuramente incluir:
- formatação e lint;
- testes unitários dos serviços;
- testes de migração de dados;
- compilação Linux;
- testes de empacotamento;
- smoke tests quando ambiente gráfico e WebKitGTK estiverem disponíveis.

A aprovação da CI não substitui testes reais no Linux Mint e em sites de referência.
