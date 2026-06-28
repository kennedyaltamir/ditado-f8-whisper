# ROADMAP DO PROJETO

O desenvolvimento do Ditado F8 Whisper está estruturado em fases. A IA deve sempre consultar este documento para entender o que ainda é futuro. **Funcionalidades listadas abaixo NÃO ESTÃO IMPLEMENTADAS (exceto as marcadas como Implementadas/preparadas).** A IA não deve inventá-las.

### Fase 1: Arquitetura de Configuração (Implementada - Preparada para validação)
* **Objetivo:** Extrair valores hardcoded, permitir configurações dinâmicas e construir a Interface Visual para edição.
* **Fase 1A - Back-end de Configuração:** Criado o arquivo `config.json`, lógica base inserida para suportar tecla flexível, modo de gravação (`hold` ou `toggle`) e tecla de segurança (`Esc`).
* **Fase 1B - Front-end de Configuração:** Adicionado botão de Configurações no Widget Principal e criado painel/modal em Tkinter (`Toplevel`).
* **Fase 1C - Aplicação dinâmica de configurações:** Atualização segura e em tempo real dos hooks de teclado global.

### Fase 2: Melhorias de Usabilidade UI/UX (Implementada - Preparada para validação)
* **Objetivo:** Dar mais feedback em tempo real para o usuário e facilitar o uso via mouse.
* **Fase 2A - Botão Visual de Gravação:** Adicionado botão "Gravar/Parar" na interface, operando de forma independente da hotkey.
* **Fase 2B - Contador de Tempo:** Adicionado timer (`MM:SS`) atualizado em tempo real durante a gravação.
* **Fase 2C - Indicador de Volume:** Adicionada barra visual que reage à captação do microfone.
* **Fase 2D - Polimento Visual:** Reorganização do layout para acomodar os novos controles mantendo a estética premium.

### Fase 3: Organização de Dados e Histórico (Próxima Fase)
* **Objetivo:** Estruturar as sessões de ditado para fácil busca e recuperação.
* **Fase 3A - Histórico no Widget:** Mostrar um histórico com os últimos textos ditados diretamente no widget, permitindo copiar ou reutilizar.
* **Fase 3B - Organização por Data:** Salvar os arquivos em subpastas organizadas por data (ex: `gravacoes_ditado/YYYY-MM-DD/`).
* **Fase 3C - Metadados:** Criar arquivo JSON de metadados consolidando áudio, texto, data e tempo.

### Fase 4: Personalização e Design (Futuro)
* **Objetivo:** Permitir ao usuário adaptar a ferramenta ao seu fluxo de trabalho.
* **Tarefas:**
  * Criar um Modo Compacto (exibindo apenas status e botões essenciais) e um Modo Expandido.
  * Opções adicionais na Tela de Configurações para: trocar microfone, modelo do Whisper, idioma e tema visual.
  * Opção de descartar o arquivo `.wav` ou transcrição após uso.

### Fase 5: Integração com Windows (System Tray e Logs)
* **Objetivo:** Comportamento nativo de aplicativo residente.
* **Tarefas:**
  * Minimizar o aplicativo para a Bandeja do Sistema (Tray Icon).
  * Opção de iniciar automaticamente com o Windows.
  * Geração de arquivos reais de logs técnicos.
  * Prevenção contra a abertura de múltiplas instâncias do script.
  * Melhoria global no tratamento de exceções.

### Fase 6: Empacotamento
* **Objetivo:** Facilidade de distribuição.
* **Tarefas:**
  * Empacotar em `.exe` com PyInstaller.
  * Criar instalador formal.
