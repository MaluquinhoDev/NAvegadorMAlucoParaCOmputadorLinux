# Plano de portabilidade para Linux

## 1. Diagnóstico do projeto Android

O repositório original é um aplicativo Android escrito em Kotlin. Ele combina:

- Android WebView como motor principal e uma atividade GeckoView separada.
- Extensões locais baseadas em content scripts JavaScript.
- Controles de atenção, bloqueio de conteúdo e personalização do YouTube.
- Reprodução e controle de mídia por AndroidX Media3.
- Tradução local com Google ML Kit.
- Persistência em APIs Android, como SharedPreferences e armazenamento privado.

A lógica de algumas extensões JavaScript é reaproveitável. As telas, serviços, permissões, armazenamento e motores Android não são portáveis diretamente para Linux Mint.

## 2. Hardware e restrições

Alvo de referência: Intel Celeron N3060, 4 GB de RAM e Linux Mint 64 bits.

Consequências de projeto:

1. Não manter um segundo motor de navegador em execução junto do Firefox.
2. Evitar Electron/Chromium empacotado como primeira solução: duplicaria processos e consumo de memória.
3. Evitar serviços residentes, sincronização em segundo plano e observadores globais desnecessários.
4. Priorizar JavaScript simples, CSS seletivo, armazenamento local e execução apenas nas páginas correspondentes.
5. Não carregar bibliotecas pesadas para funções que podem ser resolvidas pelas APIs do navegador.
6. Tratar vídeo e muitas abas como os maiores fatores variáveis de consumo; o Celeron não transforma uma página pesada em uma página leve.

## 3. Decisão arquitetural

### Primeira versão: extensão Firefox

O Firefox será o navegador hospedeiro. O projeto será uma extensão WebExtension, começando por YouTube sem distrações.

Vantagens:
- Reutiliza o motor já instalado e aberto pelo usuário.
- Evita duplicar o consumo de RAM de um navegador completo.
- Permite instalação e depuração pelo Firefox.
- Reaproveita parte do content script JavaScript original.

Limites:
- Não cria um navegador independente com marca própria.
- Não controla toda a interface do Firefox.
- Não pode reproduzir automaticamente APIs exclusivas do Android.
- As políticas de extensões e APIs variam entre Firefox e Chromium.

### Alternativas avaliadas

| Abordagem | Avaliação para 4 GB de RAM |
|---|---|
| Extensão Firefox | **Escolhida:** menor duplicação de recursos e menor superfície técnica |
| Aplicativo GTK + WebKitGTK | Possível em fase futura, mas cria outro navegador/processo e exige integração nativa |
| Tauri + WebKitGTK | Mais leve que Electron em muitos cenários, porém adiciona runtime e complexidade sem benefício inicial claro |
| Electron | Não recomendado para o hardware-alvo: inclui outro Chromium e tende a elevar o uso de memória |
| Qt WebEngine | Não recomendado como primeira versão: motor Chromium embutido e maior custo de empacotamento |

## 4. Plano por fases

### Fase 0 — Base do repositório
- [x] Registrar diagnóstico e decisão técnica.
- [x] Criar esqueleto de extensão Firefox.
- [x] Criar validação estática e empacotamento no GitHub Actions.
- [ ] Testar instalação real no Linux Mint de referência.

### Fase 1 — YouTube sem distrações
- [x] Adaptar o content script existente.
- [x] Aplicar padrões iniciais para reduzir feed, Shorts, recomendações e autoplay.
- [ ] Criar página de opções para ligar/desligar cada recurso.
- [ ] Testar vídeos longos, pesquisa, inscrições, canais e navegação SPA.
- [ ] Criar testes de regressão para os seletores mais importantes.
- [ ] Medir CPU e RAM com extensão ligada/desligada.

Critério de conclusão: controles essenciais funcionam sem quebrar pesquisa, vídeos longos e reprodução manual.

### Fase 2 — Preferências e bloqueios
- [ ] Criar interface de opções acessível e leve.
- [ ] Persistir preferências com `browser.storage.local`.
- [ ] Migrar bloqueio de domínios usando APIs WebExtensions compatíveis com Firefox.
- [ ] Separar regras de bloqueio, regras visuais e controles de navegação.
- [ ] Incluir exportação/importação local das configurações.

Critério de conclusão: preferências sobrevivem ao reinício e cada controle pode ser testado isoladamente.

### Fase 3 — Ferramentas de estudo
- [ ] Biblioteca local de vídeos.
- [ ] Marcação de timestamps.
- [ ] Anotações por vídeo.
- [ ] Temporizador de sessão.
- [ ] Velocidade por canal, com limites e fallback.
- [ ] Interface sem painel permanente quando nenhuma ferramenta estiver ativa.

Critério de conclusão: dados ficam no perfil local do Firefox e não são enviados a servidor.

### Fase 4 — Tradução e mídia
- [ ] Investigar APIs de tradução disponíveis no Firefox/Linux.
- [ ] Não presumir que Google ML Kit Android funciona no desktop.
- [ ] Definir mecanismo local ou integração explicitamente opcional.
- [ ] Verificar consumo de memória dos modelos antes de adotar tradução offline.
- [ ] Manter controles de velocidade compatíveis com players HTML5; não prometer suporte a DRM ou iframes isolados.

Critério de conclusão: mecanismo, dependências, privacidade e consumo documentados antes da implementação.

### Fase 5 — Aplicativo independente (decisão futura)
Só iniciar após as fases anteriores demonstrarem necessidade real de uma janela própria.

- [ ] Medir a extensão em uso cotidiano.
- [ ] Comparar GTK/WebKitGTK com Tauri/WebKitGTK em RAM ociosa e durante vídeo.
- [ ] Reaproveitar lógica independente do navegador, sem portar APIs Android por cópia.
- [ ] Não adotar Electron sem medição que justifique o custo.
- [ ] Definir empacotamento .deb/AppImage apenas após estabilizar o aplicativo.

## 5. Critérios de qualidade

- Compatibilidade: Firefox estável no Linux Mint 64 bits.
- Recursos: sem serviço em segundo plano quando nenhuma página compatível estiver aberta.
- Privacidade: processamento local por padrão; nenhuma coleta ou telemetria própria.
- Robustez: falha de um seletor não deve interromper o restante da extensão.
- Manutenção: cada recurso deve poder ser habilitado, desabilitado e testado separadamente.
- Desempenho: medir baseline do Firefox e diferença causada pela extensão; não usar números inventados como meta.

## 6. Fora do escopo inicial

- Reescrever o motor de navegação.
- Reimplementar GeckoView ou Android WebView para desktop.
- Replicar integralmente o Android Media3.
- Prometer bloqueio total de anúncios ou alteração do algoritmo do YouTube.
- Sincronizar dados pessoais com nuvem.
