# HISTÓRICO E CONHECIMENTO DO PROJETO

Este arquivo funciona como a memória histórica e registro de decisões arquiteturais curadas do desenvolvimento. A IA deve consultá-lo para compreender os paradigmas adotados no projeto.

---

### Registro 2: Implementação Fase 1A (Arquitetura Dinâmica) - Preparada para validação
* **Gerenciamento de Configuração Segura:** Adotamos o uso do `config.json` referenciado através de `os.path.abspath(__file__)` como base. Isso previne bugs na criação do arquivo quando a inicialização do app não ocorre a partir do diretório raiz local (ex: rodando via `pythonw.exe`).
* **Captura Global de Hotkeys:** O projeto transita do mapeamento pontual para o uso flexível do módulo `keyboard` (via `hook`), permitindo amarrar ações a combinações compostas de tecla, como `ctrl+space`. 
* **Lógica Limpa Hold/Toggle/Cancel:** Estruturado um controle de estado robusto (utilizando a flag `cancel_until_hotkey_released`) para impedir que a captura global retome a gravação imprevistamente após um cancelamento (`Esc`) caso o usuário mantenha o dedo na hotkey (Modo `hold`).
* **Preservação de UI:** O módulo de ignorar gravação em disco (`save_audio` e `save_txt`) foi intencionalmente congelado, de forma que o sistema preserva o comportamento padrão de criação, mantendo todos os botões do widget visual saudáveis enquanto a UI visual definitiva para isso não é construída.

---

### Registro 1: Definição Base e Homologação
* **Data aproximada:** Configuração Inicial.
* **Monolito Funcional:** Ficou estabelecido que o arquivo `ditado_f8_widget.py` concentra toda a lógica atual do projeto: interface gráfica (`tkinter`), atalho global (`keyboard`), controle de gravação e chamada assíncrona do motor do Whisper, descartando o `ditado_f8.py` como núcleo principal.
* **Inicialização Silenciosa:** O arquivo `Iniciar Ditado F8 Widget.vbs` está validado com o uso do `pythonw.exe`. Ele garante que o usuário consiga subir a aplicação transparente sem um console CMD aberto.
* **Modelo de Transcrição:** A orquestração do Whisper pelo Python dita que o script abre o `whisper-cli.exe` como subprocesso, lê e filtra as saídas de texto em tempo real (stdout), e o próprio Python salva o arquivo TXT em disco, garantindo a captura formatada do resultado.
* **Padrões Fixos Homologados:** O projeto, em sua fase de MVP, se apoia firmemente em caminhos absolutos no disco do usuário (`C:\whispercpp\...`) e salva os dados baseados em timestamps rígidos (`YYYYMMDD_HHMMSS.wav` e `YYYYMMDD_HHMMSS.txt`).
* **Microfone Homologado:** Iriun Webcam (validado via biblioteca `sounddevice`).
