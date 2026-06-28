# ROADMAP DO PROJETO

O desenvolvimento do Ditado F8 Whisper está estruturado em fases. A IA deve sempre consultar este documento para entender o que ainda é futuro. **Funcionalidades listadas abaixo NÃO ESTÃO IMPLEMENTADAS.** A IA não deve inventá-las.

### Fase 1: Arquitetura de Configuração (Próxima Fase)
* **Objetivo:** Extrair valores hardcoded (caminhos absolutos, teclas) e permitir configurações dinâmicas.
* **Tarefas:** 
  * Criar o arquivo `config.json`.
  * Mover os caminhos `C:\whispercpp\...` do código para o JSON.
  * Permitir configurar a tecla de atalho no JSON (tirar a obrigatoriedade do F8 fixo).
  * Criar lógica para escolher o modo de gravação: `hold` (segurar) ou `toggle` (apertar para iniciar, apertar para parar).
  * Adicionar tecla de segurança para cancelar gravação (ex: `Esc`).

### Fase 2: Melhorias de Usabilidade UI/UX
* **Objetivo:** Dar mais feedback em tempo real para o usuário.
* **Tarefas:**
  * Adicionar um botão visual "Gravar" na própria interface do widget.
  * Adicionar contador de tempo de gravação visível na tela.
  * Adicionar um indicador de volume do microfone em tempo real.

### Fase 3: Organização de Dados e Histórico
* **Objetivo:** Estruturar as sessões de ditado para fácil busca.
* **Tarefas:**
  * Mostrar um histórico com os últimos textos ditados diretamente no widget.
  * Salvar os arquivos em subpastas organizadas por data.
  * Criar um arquivo JSON de metadados consolidando áudio, texto, data e tempo de gravação.

### Fase 4: Personalização e Design
* **Objetivo:** Permitir ao usuário adaptar a ferramenta ao seu fluxo de trabalho.
* **Tarefas:**
  * Criar um Modo Compacto e um Modo Expandido.
  * Opções via JSON para: trocar microfone, modelo do Whisper, idioma, tema visual e opção de "Sempre no topo".
  * Opções de ligar/desligar auto-paste, e opção de descartar o arquivo `.wav` após uso.

### Fase 5: Integração com Windows (System Tray e Logs)
* **Objetivo:** Comportamento nativo de aplicativo residente.
* **Tarefas:**
  * Minimizar o aplicativo para a Bandeja do Sistema (Tray Icon).
  * Opção de iniciar automaticamente com o Windows.
  * Geração de arquivos reais de logs técnicos.
  * Prevenção contra a abertura de múltiplas instâncias do script.
  * Melhoria global no tratamento de exceções (try/excepts refinados).

### Fase 6: Empacotamento
* **Objetivo:** Facilidade de distribuição.
* **Tarefas:**
  * Empacotar em `.exe` com PyInstaller.
  * Criar instalador formal.
