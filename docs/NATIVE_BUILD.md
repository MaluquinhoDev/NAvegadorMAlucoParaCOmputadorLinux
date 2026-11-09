# Compilação nativa experimental

## O que a compilação muda

O projeto continua usando GTK3, PyGObject e WebKitGTK. O Nuitka traduz os módulos Python acompanhados pelo compilador para código C e gera um executável nativo. Isso não substitui o motor WebKitGTK nem recompila o JavaScript dos sites: layout, pintura, rede, codecs e grande parte da execução web continuam no WebKitGTK e em bibliotecas nativas.

O perfil usado é `--mode=accelerated`. Ele depende da instalação de Python do sistema e das bibliotecas GTK/WebKitGTK compatíveis. Não é um binário universal, não é um pacote independente e não deve substituir o pacote Debian Python atual.

## Por que é experimental

- Compilar Python não garante aceleração perceptível. O ganho tende a ser limitado quando o tempo é gasto no WebKitGTK, na rede, no JavaScript do site ou em espera de I/O.
- O modo accelerated continua dependendo do runtime Python e das bibliotecas instaladas no computador.
- PyGObject usa bindings dinâmicos para bibliotecas GObject e introspecção; por isso o executável precisa passar por teste real de inicialização GTK/WebKitGTK.
- O compilador pode aumentar o tempo de build e o tamanho do artefato. O executável compilado não é automaticamente mais leve em RAM.
- A CI constrói o executável em Ubuntu 24.04 x86_64. Isso não comprova compatibilidade com todas as versões do Linux Mint.

## Construir e testar

Dependências no Debian/Ubuntu:

```bash
sudo apt install python3 python3-gi gir1.2-gtk-3.0 gir1.2-webkit2-4.1 python3-venv python3-dev build-essential patchelf xvfb
python3 -m venv --system-site-packages .venv-nuitka
.venv-nuitka/bin/python -m pip install Nuitka
PYTHON=.venv-nuitka/bin/python bash scripts/build-native.sh
xvfb-run -a dist/native/navegador-maluco-native --smoke-test
```

O argumento `--smoke-test` abre a janela, aguarda a criação do WebView por até 15 segundos e encerra com erro se a inicialização falhar.

## Critério para substituir o pacote padrão

A versão compilada só deve substituir a versão Python depois de:
1. passar pelo smoke test em Linux Mint real;
2. preservar todos os recursos e o carregamento dos assets;
3. ser comparada com a versão Python usando as mesmas páginas, perfil e condições;
4. demonstrar melhora repetível no tempo de inicialização, resposta da interface ou CPU, sem piora relevante de RAM;
5. funcionar com a versão de Python, GTK e WebKitGTK disponível no Mint de destino.

O workflow publica o binário como artefato experimental separado. O pacote Debian padrão permanece inalterado até que esses critérios sejam comprovados.


## Pacote Debian nativo

A trilha atual gera um segundo pacote, `navegador-maluco-native`, a partir do mesmo executável Nuitka que passa pelo smoke test. Isso elimina a diferença anterior em que o artefato nativo era apenas um arquivo separado e o .deb instalava o código Python.

O pacote nativo usa o modo `accelerated`: o código Python acompanhado pelo Nuitka é compilado, mas o runtime CPython, PyGObject, GTK3 e WebKitGTK continuam sendo dependências do sistema. Por isso o pacote é `amd64` e está associado ao ambiente Ubuntu 24.04 usado no build; o alvo inicial é Linux Mint 22.x. A versão Python continua publicada como fallback e referência.

A CI agora:
1. compila o executável;
2. executa o smoke test direto;
3. monta o .deb nativo com assets, launcher e entrada de menu próprios;
4. instala o .deb no runner;
5. executa o smoke test pelo comando instalado;
6. publica o .deb nativo e o executável bruto como artefatos distintos.

O pacote nativo não substitui automaticamente o Python. A promoção exige teste no Mint real e benchmark A/B com mesmas páginas, perfil e condições. O modo `standalone` permanece uma linha experimental separada: ele empacota runtime e dependências Python, mas não deve ser adotado sem validar os bindings dinâmicos PyGObject/GObject Introspection e as bibliotecas GTK/WebKitGTK do sistema.


## Comparação automática Python versus Nuitka

O script `scripts/benchmark-startup.sh` executa cinco inicializações de cada variante com perfis XDG isolados e ambiente Xvfb idêntico. Ele mede o tempo até o smoke test detectar a primeira WebView e o pico de RSS do processo, registrando os dados em CSV. O relatório é publicado pela CI como `navegador-maluco-startup-benchmark`.

Essa medição compara somente inicialização do shell GTK/WebKitGTK no runner Ubuntu 24.04. Não mede velocidade de carregamento de sites, JavaScript, vídeo, rolagem ou desempenho no Celeron físico. Os resultados precisam ser interpretados por mediana e com a variabilidade entre execuções; não são uma prova de que o navegador inteiro ficou mais rápido.


### Resultado inicial registrado pela CI

Na execução `42706147095`, com cinco inicializações de cada variante no mesmo runner Ubuntu 24.04:
- Python: mediana de 0,37 s e pico RSS reportado de 181.552 KiB.
- Nuitka accelerated: mediana de 0,37 s e pico RSS reportado de 182.084 KiB.

A diferença observada foi de 0,00 s na mediana arredondada e +532 KiB para a versão compilada.

Uma segunda execução, `42706300869`, apresentou Python em 0,42 s / 182.108 KiB e Nuitka em 0,43 s / 183.092 KiB. A diferença foi de +0,01 s e +984 KiB. As duas amostras apontam para desempenho de inicialização praticamente empatado, com pequenas variações entre execuções; não há evidência de ganho consistente do Nuitka nesse teste. O valor de RSS vem do GNU time aplicado ao comando de smoke test; não é uma soma auditada de PSS de todos os processos WebKit. Os resultados não representam o Celeron N3060 e não medem carregamento de sites ou fluidez de rolagem.

A leitura técnica é importante: compilar o shell Python pode reduzir trabalho de inicialização do próprio código, mas o motor WebKitGTK continua responsável pela maior parte da navegação. Uma melhoria expressiva no uso real precisa ser confirmada em tarefas completas e no hardware-alvo, não presumida pelo formato do executável.
