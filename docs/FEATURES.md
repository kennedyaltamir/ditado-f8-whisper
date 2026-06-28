# FEATURES ATUAIS

Este documento lista estritamente as funcionalidades **já implementadas, aprovadas e em funcionamento** no ambiente local do usuário (no arquivo `ditado_f8_widget.py`).

## 1. Interface Gráfica Premium
* Janela customizada "Borderless" (sem as bordas padrão do Windows).
* Funcionalidade de arrastar a janela clicando no fundo.
* Botões superiores de Minimizar e Fechar embutidos na interface.
* Status visual na tela atualizado dinamicamente (Pronto, Gravando, Carregando sua voz, Texto colado, Erro).
* Exibição na tela do último texto transcrito.
* Exibição do nome do último arquivo de áudio e último arquivo de texto gerados.

## 2. Ações do Widget (Botões)
* **Abrir Pasta:** Abre imediatamente a pasta `C:\whispercpp\gravacoes_ditado`.
* **Ouvir Áudio:** Toca o último arquivo `.wav` gravado pelo usuário.
* **Abrir TXT:** Abre o último arquivo `.txt` gerado no editor padrão do Windows.
* **Copiar Texto:** Joga o conteúdo transcrito novamente na área de transferência.

## 3. Motor de Gravação e Atalho Global
* Hook global da tecla `F8` via biblioteca `keyboard`.
* **Modo Hold:** A gravação de áudio ocorre exclusivamente enquanto a tecla `F8` está sendo pressionada. Ao soltar, a gravação é encerrada imediatamente.
* Arquivos salvos rigorosamente no padrão de timestamp: `YYYYMMDD_HHMMSS.wav` e `YYYYMMDD_HHMMSS.txt`.

## 4. Orquestração do Whisper e Colagem
* Chamada do executável `whisper-cli.exe` (usando o modelo `ggml-medium.bin` e `language=pt`) em uma Thread secundária para não travar o loop do `tkinter`.
* Parsing do `stdout/stderr` do Whisper feito pelo Python.
* Cópia do texto tratado para a área de transferência do Windows (`pyperclip`).
* Execução automatizada de `Ctrl+V` para colar o texto onde o cursor do usuário estiver posicionado.

## 5. Inicialização Limpa
* Inicialização silenciosa via arquivo `Iniciar Ditado F8 Widget.vbs` executando o `pythonw.exe`.
