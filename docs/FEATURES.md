# FEATURES ATUAIS

Este documento lista estritamente as funcionalidades **já implementadas, preparadas para validação e em funcionamento** no ambiente local do usuário (no arquivo `ditado_f8_widget.py`).

## 1. Interface Gráfica Premium e Controles Visuais (Fase 2)
* Janela customizada "Borderless" (sem as bordas padrão do Windows).
* Funcionalidade de arrastar a janela clicando no fundo.
* Botões superiores de Minimizar, Fechar e **Configurações (⚙)** embutidos na interface.
* **Botão Visual de Gravação:** Permite iniciar e parar a gravação diretamente pelo mouse, funcionando como um toggle independente da configuração da hotkey.
* **Botão de Cancelamento Visual:** Permite abortar a gravação em andamento com um clique.
* **Contador de Tempo:** Exibe a duração da gravação em tempo real (`MM:SS`).
* **Indicador de Volume:** Barra visual (`████░░░░`) que reage à captação do microfone em tempo real.
* Status visual na tela atualizado dinamicamente.
* Exibição na tela do último texto transcrito.
* Exibição do nome do último arquivo de áudio e último arquivo de texto gerados.
* Exibição em **Badge (Destaque)** da Hotkey atual e do Modo de Gravação no painel de status do widget.

## 2. Interface de Configurações (Fase 1B e 1C)
* Janela de configurações acessível diretamente no Widget.
* Permite modificar a tecla de ativação (`f8`, `f9`, `ctrl+space`, etc).
* Permite modificar o Modo de Gravação (Segurar para falar ou Apertar para iniciar/parar).
* Permite modificar a Tecla de cancelamento de gravação (`esc`, `f12`, etc).
* Permite habilitar/desabilitar a "Colagem Automática" após a transcrição.
* Permite habilitar/desabilitar o comportamento de "Manter widget sempre no topo".
* **Aplicadas em tempo real:** Todas as alterações são validadas e atualizadas imediatamente (variáveis de estado, engine global de hooks e interface) sem a necessidade de reiniciar o aplicativo.
* Validações ativas impedem edições durante gravações ou caso teclas conflitantes sejam selecionadas.
* Botão para Salvar e Botão para Abrir o `config.json` manualmente.

## 3. Ações do Widget (Botões)
* **Abrir Pasta:** Abre imediatamente a pasta de gravações (configurável).
* **Ouvir Áudio:** Toca o último arquivo `.wav` gravado pelo usuário.
* **Abrir TXT:** Abre o último arquivo `.txt` gerado no editor padrão do Windows.
* **Copiar Texto:** Joga o conteúdo transcrito novamente na área de transferência.

## 4. Motor de Gravação e Atalhos Globais
* Arquivo `config.json` atuando como central de configuração do comportamento da aplicação.
* Tecla de atalho principal flexível configurável via Interface/JSON.
* **Modo Hold (Segurar):** A gravação ocorre exclusivamente enquanto a tecla está sendo pressionada.
* **Modo Toggle (Alternar):** A gravação inicia com um aperto e termina com o aperto subsequente da tecla.
* **Cancelamento (Esc):** Possibilidade de interromper uma gravação e descartar o áudio instantaneamente, abortando a chamada ao motor do Whisper. Inclui trava segura para o modo `hold`.
* Arquivos salvos rigorosamente no padrão de timestamp: `YYYYMMDD_HHMMSS.wav` e `YYYYMMDD_HHMMSS.txt`.

## 5. Orquestração do Whisper e Colagem
* Chamada do executável `whisper-cli.exe` em uma Thread secundária para não travar o loop do `tkinter`.
* Parsing do `stdout/stderr` do Whisper feito pelo Python.
* Cópia do texto tratado para a área de transferência do Windows (`pyperclip`).
* Execução automatizada de `Ctrl+V` para colar o texto onde o cursor do usuário estiver posicionado (controlável pela configuração `auto_paste`).

## 6. Inicialização Limpa
* Inicialização silenciosa via arquivo `Iniciar Ditado F8 Widget.vbs` executando o `pythonw.exe`.
