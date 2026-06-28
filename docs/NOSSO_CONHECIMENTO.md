# HISTÓRICO E CONHECIMENTO DO PROJETO

Este arquivo funciona como a memória histórica e registro de decisões arquiteturais curadas do desenvolvimento. A IA deve consultá-lo para compreender os paradigmas adotados no projeto.

---

### Registro 4: Implementação Fase 1C (Aplicação Dinâmica de Configurações) - Preparada para validação
* **Recarregamento de Hooks Globais:** A substituição das configurações de tecla no front-end foi atualizada para alterar o comportamento em tempo real, livrando o usuário da necessidade de reiniciar o aplicativo. Isso foi feito implementando métodos dedicados (`unregister_hotkeys` e `register_hotkeys`), que removem seguramente a escuta global do módulo `keyboard` e reativam com as novas variáveis.
* **Prevenção de Estado Inconsistente:** Alterações de configuração e chamadas ao JSON estão estritamente bloqueadas se a aplicação estiver no estado de gravação (`is_recording`) ou transcrição (`is_processing`). Além disso, as variáveis de tracking do toggle (`is_hotkey_pressed`) são resetadas a cada `register_hotkeys()` para garantir um ciclo limpo a partir de mudanças da interface.
* **Normalização Visual da Resposta:** A interface Tkinter (`Toplevel`) da aba de configurações agora provê respostas de sucesso não bloqueantes no rodapé, ao invés de janelas pop-up (`messagebox`) intrusivas que interrompem o fluxo quando a operação é bem-sucedida.

---

### Registro 3: Implementação Fase 1B (Interface de Configurações / Front-end do Widget) - Preparada para validação
* **Integração Visual de Configuração:** Implementado um modal `Toplevel` no `ditado_f8_widget.py` focado exclusivamente na edição das preferências do usuário via UI nativa. O modal gerencia a gravação direta no arquivo `config.json`.
* **Polimento do Widget Base:** Ajustes finos nas dimensões e estruturação de badges visuais (`self.badge_var`) foram feitos para tornar o widget mais elegante e claro quanto ao estado atual (Modo Hold vs Toggle e qual tecla está ativa).

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
