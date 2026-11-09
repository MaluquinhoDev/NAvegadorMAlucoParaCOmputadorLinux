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
