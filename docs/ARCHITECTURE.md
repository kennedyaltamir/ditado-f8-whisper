# ARQUITETURA DO SISTEMA

A arquitetura atual do **Ditado F8 Whisper** é centralizada e orientada a eventos, visando resolver todo o fluxo de operação em um único arquivo principal funcional, rodando em background com apoio de threads.

## 1. Estrutura e Papel dos Arquivos Principais

* **`ditado_f8_widget.py` (Núcleo Principal / Monolito Atual):** 
  Este é o arquivo central e mais importante do projeto. Ele concentra TODA a operação:
  - Cria e gerencia a interface gráfica (UI) via `tkinter` (janela sem borda, arraste, status visual, botões).
  - Configura o hook global da hotkey F8 via `keyboard`.
  - Captura o áudio do microfone.
  - Salva o arquivo `.wav`.
  - Chama o `whisper-cli.exe` em uma thread separada.
  - Captura a saída do Whisper, extrai o texto, salva o `.txt`.
  - Manipula o clipboard (`pyperclip`) e envia o `Ctrl+V`.

* **`ditado_f8.py` (Versão Legada / Core Simples):** 
  Trata-se de uma versão anterior, mais simples ou de testes. Não é o arquivo executado no fluxo principal do usuário hoje. A IA deve focar suas implementações no `ditado_f8_widget.py`.

* **`Iniciar Ditado F8 Widget.vbs`:** 
  Script de inicialização silenciosa. Sua função é executar o `ditado_f8_widget.py` utilizando o `pythonw.exe`. Isso impede que o terminal (CMD) do Windows abra ou fique visível, garantindo a experiência de um aplicativo desktop nativo.

* **`Iniciar Ditado F8.bat`:** 
  Versão antiga/alternativa de inicialização via prompt de comando, utilizada para debugar ou rodar com o terminal visível.

## 2. O Fluxo de Extração do Whisper
O fluxo de transcrição possui uma característica importante: **não é o `whisper-cli.exe` que salva o TXT no disco**. O fluxo real é:
1. O Python grava e salva o `.wav`.
2. O Python abre um subprocesso chamando o `whisper-cli.exe`, passando o `.wav`.
3. O Python captura as saídas de texto (stdout/stderr) geradas pelo Whisper em tempo real.
4. O Python filtra a string recebida (removendo tags indesejadas).
5. O **próprio Python** salva o resultado limpo em um arquivo `.txt`.
6. O Python copia o texto gerado e simula a colagem.

## 3. Pastas e Arquivos Isolados (Ignorados pelo Git)
* `whisper-bin-x64/` (Binários do Whisper e Modelos `.bin`)
* `gravacoes_ditado/` (Arquivos temporários e salvamentos gerados)
* `__pycache__/` e `.history/`
