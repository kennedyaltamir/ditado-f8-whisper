# HISTÓRICO E CONHECIMENTO DO PROJETO

Este arquivo funciona como a memória histórica e registro de decisões arquiteturais curadas do desenvolvimento. A IA deve consultá-lo para compreender os paradigmas adotados no projeto.

---

### Registro 6: Implementação Fase 3A (Histórico Recente em Memória) - Preparada para validação
* **Histórico em Memória:** Implementada uma lista visual dos últimos ditados da sessão atual. A lista é mantida estritamente em memória (`self.history_items`), sem a utilização de SQLite ou persistência complexa nesta fase.
* **Segurança de Arquivos:** O botão "Limpar" apaga apenas a lista visual da interface. Ele foi projetado para **nunca** deletar os arquivos `.wav` ou `.txt` gerados no disco, garantindo a integridade dos dados do usuário.
* **Thread Safety na UI:** A adição de novos itens ao histórico ocorre logo após a transcrição (que roda em uma thread secundária). Para evitar travamentos no Tkinter, a atualização da lista e a renderização dos novos widgets são envelopadas em uma função e despachadas para a thread principal usando `self.root.after(0, update)`.
* **Prevenção de Bugs de Closure (Lambda):** Os botões de ação de cada item do histórico (Copiar, TXT, Usar) utilizam o padrão `lambda it=item: self.action(it)` para garantir que cada botão referencie corretamente o seu respectivo item, evitando o clássico bug de loop do Python onde todos os botões apontariam para o último elemento.

---

### Registro 5: Implementação Fase 2 (Usabilidade e Feedback Visual) - Preparada para validação
* **Botão Visual de Gravação:** Implementado um botão "Gravar/Parar" na interface. Arquiteturalmente, ele reaproveita os métodos `start_recording` e `stop_and_process`, funcionando como um "toggle" por clique, independentemente de a hotkey estar configurada como `hold` ou `toggle`.
* **Thread Safety no Tkinter (Timer e Volume):** Para evitar travamentos na interface, o contador de tempo e o indicador de volume foram implementados utilizando o método `root.after()`. 
* **Cálculo de Volume (RMS):** O indicador de volume não atualiza a UI diretamente de dentro do callback do `sounddevice` (o que causaria falhas de thread). Em vez disso, o callback apenas calcula o RMS (Root Mean Square) do frame de áudio atual e salva em uma variável float (`self.current_volume`). O loop do Tkinter (`root.after`) lê essa variável a cada 100ms e desenha a barra visual.
* **Preparação para o Futuro:** As Fases 3 (Histórico e Organização por Data) e 4 (Modo Compacto) foram intencionalmente postergadas e mantidas apenas na documentação para garantir a estabilidade desta entrega focada em usabilidade.

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
