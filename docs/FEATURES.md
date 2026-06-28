# FEATURES ATUAIS

Este documento lista estritamente as funcionalidades **já implementadas, preparadas para validação e em funcionamento** no ambiente local do usuário (no arquivo `ditado_f8_widget.py`).

## 1. Interface Gráfica Premium
* Janela customizada "Borderless" (sem as bordas padrão do Windows).
* Funcionalidade de arrastar a janela clicando no fundo.
* Botões superiores de Minimizar e Fechar embutidos na interface.
* Status visual na tela atualizado dinamicamente.
* Exibição na tela do último texto transcrito.
* Exibição do nome do último arquivo de áudio e último arquivo de texto gerados.
* Exibição da Hotkey atual e Modo de Gravação (Hold/Toggle) diretamente no status do widget.

## 2. Ações do Widget (Botões)
* **Abrir Pasta:** Abre imediatamente a pasta de gravações (configurável).
* **Ouvir Áudio:** Toca o último arquivo `.wav` gravado pelo usuário.
* **Abrir TXT:** Abre o último arquivo `.txt` gerado no editor padrão do Windows.
* **Copiar Texto:** Joga o conteúdo transcrito novamente na área de transferência.

## 3. Motor de Gravação e Atalhos Globais (Fase 1A Adicionada)
* Arquivo `config.json` atuando como central de configuração do comportamento da aplicação.
* Tecla de atalho principal flexível configurável via JSON (ex: `f8`, `f9`, `ctrl+space`).
* **Modo Hold (Segurar):** A gravação ocorre exclusivamente enquanto a tecla está sendo pressionada.
* **Modo Toggle (Alternar):** A gravação inicia com um aperto e termina com o aperto subsequente da tecla.
* **Cancelamento (Esc):** Possibilidade de interromper uma gravação e descartar o áudio instantaneamente, abortando a chamada ao motor do Whisper. Inclui trava segura para o modo `hold`.
* Arquivos salvos rigorosamente no padrão de timestamp: `YYYYMMDD_HHMMSS.wav` e `YYYYMMDD_HHMMSS.txt`.

## 4. Orquestração do Whisper e Colagem
* Chamada do executável `whisper-cli.exe` em uma Thread secundária para não travar o loop do `tkinter`.
* Parsing do `stdout/stderr` do Whisper feito pelo Python.
* Cópia do texto tratado para a área de transferência do Windows (`pyperclip`).
* Execução automatizada de `Ctrl+V` para colar o texto onde o cursor do usuário estiver posicionado (possibilidade de desativar auto_paste via `config.json`).

## 5. Inicialização Limpa
* Inicialização silenciosa via arquivo `Iniciar Ditado F8 Widget.vbs` executando o `pythonw.exe`.
