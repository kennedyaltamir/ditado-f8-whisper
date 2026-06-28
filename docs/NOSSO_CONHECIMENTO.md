# HISTÓRICO E CONHECIMENTO DO PROJETO

Este arquivo funciona como a memória histórica e registro de decisões arquiteturais curadas do desenvolvimento. A IA deve consultá-lo para compreender os paradigmas adotados no projeto.

---

### Registro 1: Definição Base e Homologação
* **Data aproximada:** Configuração Inicial.
* **Monolito Funcional:** Ficou estabelecido que o arquivo `ditado_f8_widget.py` concentra toda a lógica atual do projeto: interface gráfica (`tkinter`), atalho global (`keyboard`), controle de gravação e chamada assíncrona do motor do Whisper, descartando o `ditado_f8.py` como núcleo principal.
* **Inicialização Silenciosa:** O arquivo `Iniciar Ditado F8 Widget.vbs` está validado com o uso do `pythonw.exe`. Ele garante que o usuário consiga subir a aplicação transparente sem um console CMD aberto.
* **Modelo de Transcrição:** A orquestração do Whisper pelo Python dita que o script abre o `whisper-cli.exe` como subprocesso, lê e filtra as saídas de texto em tempo real (stdout), e o próprio Python salva o arquivo TXT em disco, garantindo a captura formatada do resultado.
* **Padrões Fixos Homologados:** O projeto, em sua fase de MVP, se apoia firmemente em caminhos absolutos no disco do usuário (`C:\whispercpp\...`) e salva os dados baseados em timestamps rígidos (`YYYYMMDD_HHMMSS.wav` e `YYYYMMDD_HHMMSS.txt`).
* **Microfone Homologado:** Iriun Webcam (validado via biblioteca `sounddevice`).
* **Próximas Prioridades:** Conduzir a migração para a **Fase 1** (criação do `config.json` para suportar diferentes hotkeys, modos de toggle e flexibilidade de caminhos), garantindo que as implementações futuras não quebrem a fluidez do monolito já existente.
