# HANDOFF_DITADO_F8.md

> Projeto: Ditado F8 Whisper  
> Repositório: `kennedyaltamir/ditado-f8-whisper`  
> Branch de trabalho: `update`  
> Branch base: `main`  
> SHA-base de `main`: `c65fe91b60f2142afa3338f20874535610562e11`  
> Último commit funcional antes desta atualização documental: `0278f2ccb657b0b777d20b20171b2bc301354bfc`  
> Data: 2026-09-15

---

## 1. Identificação do projeto

Aplicação desktop local para Windows 11, escrita em Python, destinada a capturar áudio por hotkey ou botão, transcrever localmente com `whisper.cpp` (`whisper-cli.exe`) e disponibilizar o texto via clipboard/auto-paste.

Fluxo funcional principal a preservar:

`F8 -> gravação -> Whisper local -> texto -> clipboard/colagem`

Comportamentos a preservar:

- modo hold;
- modo toggle;
- botão visual;
- cancelamento;
- histórico;
- configuração;
- inicialização silenciosa;
- WAV/TXT conforme configuração;
- processamento local/offline.

---

## 2. Estado da branch

### Remoto — VERIFICADO

- `main`: `c65fe91b60f2142afa3338f20874535610562e11`;
- `update`: `0278f2ccb657b0b777d20b20171b2bc301354bfc` antes deste commit documental;
- `update` está 9 commits à frente e 0 atrás de `main`;
- merge-base permanece `c65fe91b60f2142afa3338f20874535610562e11`;
- `main` não recebeu alterações deste trabalho.

### Local do usuário — ÚLTIMO ESTADO INFORMADO

- branch: `update`;
- último HEAD local confirmado antes de `0278f2c`: `19f69e5f92d76992a1219e0b7d05505cce53d1ed`;
- `config.json` possui alteração local intencional de `recording_mode: toggle -> hold`;
- essa alteração local deve ser preservada e não deve ser descartada automaticamente.

---

## 3. Último commit validado

Último commit funcional remoto antes desta atualização:

`0278f2ccb657b0b777d20b20171b2bc301354bfc` — `fix: corrigir semantica de transcricao vazia nos logs`

Validação desse commit:

- `IMPLEMENTADO`;
- `VERIFICADO ESTATICAMENTE` por compilação Python em ambiente de análise;
- smoke test confirmou que `whisper_empty -> transcript_available("nenhum")` passa a ser registrado semanticamente como `transcript_empty_display` com `text_length=0`, `empty=true`;
- `NÃO TESTADO` ainda no Windows do usuário após esse commit específico.

Commits relevantes da `update`:

1. `f73fc9d99923fc7604eee00e009ca45c11fe4bd3` — `docs: criar handoff tecnico inicial da branch update`;
2. `618badb6744f411d33e01ded21991ee474383ee0` — `refactor: adicionar dispatcher de eventos e estado inicial`;
3. `bdf49166b834f01c47e92c525a90e2e9420fb4c8` — `refactor: iniciar widget pelo dispatcher de eventos`;
4. `261bcb2e124c12cd841bf2e09489ef2a74e39821` — `fix: iniciar app a partir do diretorio do launcher`;
5. `d4fb0c7cefdafd9d3e2d04700815ede1939e1552` — `docs: atualizar handoff com estado parcial do m2`;
6. `776676eba07e95e6cd18ab5bcc4ade9b33068f82` — `feat: adicionar logging estruturado local`;
7. `56b1e59e27fb537b4699c8140fa40a063c643d8c` — `feat: instrumentar fluxo principal com logs estruturados`;
8. `19f69e5f92d76992a1219e0b7d05505cce53d1ed` — `fix: registrar clipboard e autopaste no logging`;
9. `0278f2ccb657b0b777d20b20171b2bc301354bfc` — `fix: corrigir semantica de transcricao vazia nos logs`.

---

## 4. Objetivo do projeto

Evoluir o MVP funcional para uma aplicação desktop local robusta, determinística, testável, diagnosticável, portátil e preparada para futura distribuição, sem regressão do fluxo funcional existente.

A evolução deve continuar incremental, verificável e reversível.

---

## 5. Arquitetura atual

O núcleo funcional continua concentrado em `ditado_f8_widget.py`, que ainda reúne:

- UI Tkinter;
- configuração;
- captura de áudio;
- seleção de dispositivo;
- gravação/cancelamento;
- persistência WAV/TXT;
- execução do Whisper;
- parsing;
- histórico;
- clipboard/auto-paste;
- shutdown legado.

M2 introduziu `ditado_f8_app.py` como controlador/entrypoint transitório.

Esse módulo adiciona:

- `AppState`;
- `AppEvent`;
- `queue.SimpleQueue`;
- publicação de eventos pelo hook global;
- drenagem no loop Tk via `root.after`;
- despacho centralizado;
- bloqueio de operações depois do início do fechamento;
- estados `IDLE`, `RECORDING`, `PROCESSING`, `CANCELLING`, `ERROR`, `SHUTTING_DOWN`, `CLOSED`.

Também foi introduzido `logging_service.py`:

- logging JSON local;
- arquivo `logs/ditado_f8.log`;
- rotação aproximada em 2 MiB;
- até 5 backups;
- saída também no console quando disponível;
- instrumentação de clipboard e `Ctrl+V`;
- sem registrar o texto integral transcrito por padrão.

A arquitetura ainda é transitória: gravação, Whisper, armazenamento e parte do shutdown continuam delegados ao `DitadoWidget` legado.

---

## 6. Arquitetura alvo

Componentes-alvo, sem reescrita total:

- `AppController`;
- `HotkeyController`;
- `RecordingService`;
- `AudioDeviceService`;
- `WhisperService`;
- `WhisperOutputParser`;
- `StorageService`;
- `HistoryService`;
- `OutputController`;
- `ConfigService`;
- `LoggingService`;
- `ShutdownController`.

Fluxo-alvo:

`UI -> Event Dispatch -> AppController -> RecordingService -> WhisperService -> StorageService -> OutputController -> UI`

---

## 7. Fluxo operacional

### Hold

`HOTKEY_DOWN -> dispatcher -> RECORDING -> HOTKEY_UP -> PROCESSING -> Whisper -> output -> IDLE`

Status: `TESTADO PELO USUÁRIO / PASS`.

Logs confirmaram eventos publicados inicialmente pelo thread do `keyboard` e processados pelo `MainThread`.

### Toggle

`HOTKEY_DOWN -> RECORDING -> HOTKEY_DOWN seguinte -> PROCESSING -> IDLE`

Status: `TESTADO PELO USUÁRIO / PASS` em teste manual anterior.

### Botão visual

`BUTTON_START -> RECORDING -> BUTTON_STOP -> PROCESSING -> IDLE`

Status: `TESTADO PELO USUÁRIO / PASS`.

### Cancelamento

`CANCEL -> CANCELLING -> descarte -> IDLE`

Status: `IMPLEMENTADO / NÃO TESTADO` manualmente após M2.

### Fechamento normal

`APPLICATION_CLOSE -> SHUTTING_DOWN -> CLOSED -> mainloop exit`

Status: `TESTADO PELO USUÁRIO / PASS` quando o app está em `IDLE`.

### Clipboard/auto-paste

Fluxo observado:

`transcript_available -> output_copy -> output_paste(ctrl+v) -> Texto colado -> Pronto`

Status: `TESTADO PELO USUÁRIO / PASS`.

Importante: isso comprova a chamada real de clipboard e teclado. Ainda não comprova programaticamente que o destino restaurado é sempre a janela correta; F05 continua pendente.

---

## 8. Máquina de estados

Estados atuais:

- `IDLE`;
- `RECORDING`;
- `PROCESSING`;
- `CANCELLING`;
- `ERROR`;
- `SHUTTING_DOWN`;
- `CLOSED`.

Eventos atuais:

- `HOTKEY_DOWN`;
- `HOTKEY_UP`;
- `BUTTON_START`;
- `BUTTON_STOP`;
- `CANCEL`;
- `APPLICATION_CLOSE`.

Eventos ainda não modelados de forma explícita no dispatcher:

- `RECORD_LIMIT_REACHED`;
- `RECORDING_ERROR`;
- `TRANSCRIPTION_SUCCESS`;
- `TRANSCRIPTION_EMPTY`;
- `TRANSCRIPTION_ERROR`;
- `TRANSCRIPTION_TIMEOUT`.

Classificação: `PARCIAL`.

A FSM ainda observa `self.is_processing` do legado para retornar de `PROCESSING` a `IDLE`.

Teste real já mostrou que `HOTKEY_DOWN/HOTKEY_UP` recebidos durante `PROCESSING` são despachados e ignorados sem iniciar nova gravação. Isso valida parcialmente a idempotência/bloqueio de eventos incompatíveis.

---

## 9. Componentes principais

### `ditado_f8_app.py`

Controlador transitório, event dispatcher, FSM parcial e pontos de instrumentação do fluxo.

### `ditado_f8_widget.py`

Monólito funcional herdado, ainda responsável pelas operações concretas de áudio, Whisper, persistência, UI e output.

### `logging_service.py`

`IMPLEMENTADO`. Logging JSON rotativo, console + arquivo, instrumentação real de clipboard/teclado e proteção de privacidade.

### `config.json`

Configuração ativa. Ainda é versionada e contém caminhos específicos do ambiente.

### `Iniciar Ditado F8 Widget.vbs`

Launcher silencioso. Resolve `ditado_f8_app.py` pela pasta do próprio VBS. O caminho do interpretador Python ainda é absoluto.

### `Iniciar Ditado F8.bat`

Launcher legado para `ditado_f8.py`.

### `ditado_f8.py`

Implementação legada ainda referenciada pelo BAT.

### `ditado_f8_widget_backup_controle.py`

Backup versionado ainda não removido.

---

## 10. Problemas conhecidos

### F01 — CRITICAL — fronteira `keyboard -> Tkinter`

`PARCIALMENTE CORRIGIDO / TESTADO PELO USUÁRIO`.

No entrypoint atual o hook global publica eventos; gravação/UI são disparadas pelo dispatcher no `MainThread`. Logs reais confirmaram a fronteira em hold.

Pendência: callbacks vindos da thread de processamento ainda executam métodos do widget que podem agendar ou tocar UI indiretamente e precisam ser desacoplados nos próximos marcos.

### F02 — HIGH — ausência de limite máximo de gravação

`PENDENTE`.

### F03 — HIGH — caminhos específicos de ambiente

`PENDENTE`.

### F04 — HIGH — launcher VBS não portátil

`PARCIALMENTE CORRIGIDO`.

Script é relativo ao VBS; Python ainda é absoluto.

### F05 — HIGH — foco da janela de destino

`PENDENTE`.

O `output_paste` real foi comprovado, mas não há captura/restauração/validação da janela de destino.

### F06 — HIGH — resultado Whisper sem semântica estruturada

`PENDENTE`.

O logging diferencia `whisper_success`, `whisper_empty` e exceções, mas `transcribe_wav()` ainda retorna apenas `str`.

### F07 — MEDIUM — parser Whisper acoplado

`PENDENTE`.

### F08 — MEDIUM — colisão potencial de nomes

`PENDENTE`.

### F09 — MEDIUM — microfone resolvido apenas na inicialização

`PENDENTE`.

### F10 — MEDIUM — status do callback de áudio ignorado

`PENDENTE`.

### F11 — MEDIUM — estado compartilhado por booleanos

`PARCIALMENTE CORRIGIDO`.

Existe `AppState`, mas ainda há dependência de `is_recording` e `is_processing` do legado.

### F12 — MEDIUM — shutdown não coordenado

`PARCIAL`.

Fechamento normal em `IDLE` está testado. Fechamento durante `RECORDING`/`PROCESSING` e resultado tardio continuam não testados.

### F13 — MEDIUM — Whisper sem timeout

`PENDENTE`.

### F14 — MEDIUM — configuração sem schema/versionamento

`PENDENTE`.

### F15 — MEDIUM — dependências não formalizadas

`PENDENTE`.

### F16 — MEDIUM — testes automatizados ausentes

`PENDENTE`.

### F17 — MEDIUM — ausência de logging estruturado

`CORRIGIDO PARCIALMENTE / TESTADO PELO USUÁRIO`.

Existe `LoggingService` funcional e eventos principais foram validados em Windows. Ainda faltam cobertura automatizada e eventos de futuras funcionalidades (`timeout`, `record_limit`, etc.).

### F18/F25 — HIGH — flags de persistência não controlam persistência

`PENDENTE`.

### F19 — MEDIUM — histórico baseado em dicionários

`PENDENTE`.

### F20 — LOW — backup versionado

`PENDENTE DE REVISÃO`.

### F21 — LOW — implementação legada paralela

`PENDENTE DE REVISÃO`.

### F22 — LOW — `keyboard.unhook_all()` amplo

`PENDENTE`.

### F23 — LOW — conversão float -> int16 sem clamp

`PENDENTE`.

### F24 — ARCHITECTURAL — `process_audio()` concentra responsabilidades

`PENDENTE`.

### F26 — MEDIUM — idempotência dos eventos

`PARCIALMENTE IMPLEMENTADO / PARCIALMENTE TESTADO`.

Já observado em log:

- eventos de hotkey durante `PROCESSING` não iniciaram nova gravação;
- retorno posterior para `IDLE` ocorreu normalmente.

Ainda faltam testes explícitos de:

- `HOTKEY_DOWN` duplicado na mesma pressão;
- `HOTKEY_UP` sem gravação;
- `CANCEL` duplicado;
- `STOP` após `CANCEL`;
- fechamento durante `RECORDING`;
- fechamento durante `PROCESSING`;
- callback/resultado tardio após shutdown.

### F27 — MEDIUM — configuração de preferência suja o working tree

`NOVO ACHADO`.

O usuário alterou `recording_mode` pela aplicação/configuração e `config.json` ficou modificado no checkout Git. Configuração de ambiente/preferência ainda está misturada com configuração versionada do produto.

Deve ser resolvido em M8/ConfigService, sem descartar a alteração local atual.

---

## 11. Problemas críticos

Ordem operacional atual:

1. concluir validação de M2, especialmente cancelamento e eventos inválidos restantes;
2. corrigir shutdown durante gravação/processamento e callbacks tardios;
3. M3: isolar `RecordingService` e `AudioDeviceService`;
4. M4/M5: estruturar Whisper, parser, timeout e classificação de falhas;
5. limite máximo de gravação;
6. foco seguro/output;
7. persistência coerente com flags;
8. ConfigService/versionamento;
9. formalização de dependências e testes.

---

## 12. Melhorias implementadas

### M1 — CONCLUÍDO

- branch `update` criada a partir do `main` correto;
- handoff criado;
- base e diff verificados;
- sincronização local por fast-forward validada.

### M2 — PARCIAL

Implementado:

- dispatcher de eventos;
- FSM parcial;
- boundary do hook global para fila;
- bloqueio de eventos incompatíveis por estado;
- novo entrypoint;
- launcher atualizado.

Testado:

- startup;
- toggle;
- hold;
- botão;
- Whisper real;
- auto-paste;
- retorno a `IDLE`;
- fechamento normal pelo `X`;
- parte do comportamento em `PROCESSING`.

Pendente para concluir:

- cancelamento;
- idempotência restante;
- análise de fechamento durante gravação/processamento.

### LoggingService — IMPLEMENTADO ANTECIPADAMENTE

Embora previsto originalmente para M10, foi implementado por solicitação do usuário durante M2 para melhorar diagnóstico dos próximos marcos.

Inclui:

- JSON por linha;
- arquivo local rotativo;
- console;
- eventos de aplicação, config, microfone, hotkeys, estados, gravação, storage, Whisper, histórico, clipboard, paste e shutdown;
- ausência de texto integral por padrão;
- correção de semântica de transcrição vazia.

---

## 13. Melhorias pendentes

### Para concluir M2

- testar cancelamento por ESC;
- testar cancelamento pelo botão;
- testar CANCEL duplicado/STOP após cancelamento;
- decidir se fechamento durante `RECORDING`/`PROCESSING` será corrigido ainda como estabilização de M2 ou imediatamente antes de M3;
- retestar a correção de log de transcrição vazia quando houver caso vazio reproduzível.

### M3

Isolar `RecordingService` e `AudioDeviceService` sem mudar comportamento observável.

### M4+

Ainda não iniciar até concluir os critérios mínimos de M2.

---

## 14. Testes executados

### VERIFICADO ESTATICAMENTE

- relação `main...update`;
- revisão de diffs;
- compilação/importação de `ditado_f8_app.py`, `ditado_f8_widget.py` e `logging_service.py` em etapas relevantes;
- smoke test do formatter/logging;
- smoke test da semântica `whisper_empty -> transcript_empty_display`.

### TESTADO PELO USUÁRIO — Windows 11 / Python 3.10.6

Confirmado:

- `py_compile`: PASS;
- import: PASS;
- startup: PASS;
- fechamento normal pelo `X`: PASS;
- modo toggle: PASS;
- modo hold: PASS;
- botão visual start/stop: PASS;
- microfone Iriun detectado: PASS;
- gravação real: PASS;
- Whisper real: PASS;
- `whisper_success`: PASS;
- persistência WAV: PASS no fluxo atual;
- persistência TXT: PASS no fluxo atual;
- `transcript_available`: PASS;
- histórico em memória: PASS no fluxo observado;
- `output_copy`: PASS;
- `output_paste` com `ctrl+v`: PASS;
- texto colado em Notepad: PASS manualmente;
- retorno `PROCESSING -> IDLE`: PASS;
- fechamento `IDLE -> SHUTTING_DOWN -> CLOSED`: PASS;
- arquivo `logs/ditado_f8.log`: PASS;
- eventos críticos de logging: PASS;
- privacidade: frase completa de teste não encontrada no log: PASS;
- evento incompatível de hotkey durante `PROCESSING`: ignorado sem iniciar nova gravação.

Também foi observado um caso real `whisper_empty`; o funcionamento visual retornou a `Pronto`. Esse caso revelou a inconsistência de logging posteriormente corrigida em `0278f2c`.

---

## 15. Testes não executados

**NÃO TESTADO / ainda pendente:**

- cancelamento por ESC após M2;
- cancelamento pelo botão após M2;
- CANCEL duplicado;
- STOP após CANCEL;
- fechamento durante `RECORDING`;
- fechamento durante `PROCESSING`;
- resultado tardio após shutdown;
- timeout do Whisper;
- limite máximo de gravação;
- microfone inválido/desconectado;
- executável Whisper inválido;
- modelo inválido;
- restauração segura de foco;
- `save_audio=false`;
- `save_txt=false`;
- testes automatizados;
- reteste Windows do commit `0278f2c` para transcrição vazia.

---

## 16. Dependências

Externas confirmadas:

- `keyboard`;
- `numpy`;
- `pyperclip`;
- `sounddevice`.

Biblioteca padrão relevante:

- Tkinter;
- `queue`;
- `enum`;
- `wave`;
- `threading`;
- `subprocess`;
- `winsound`;
- `logging`;
- `logging.handlers`.

Dependência externa local:

- `whisper-cli.exe`;
- modelo GGML.

Formalização em `requirements.txt`/`pyproject.toml`: `PENDENTE`.

---

## 17. Configuração

Chaves atuais:

- `hotkey`;
- `cancel_hotkey`;
- `recording_mode`;
- `microphone_name_contains`;
- `whisper_dir`;
- `whisper_exe`;
- `model_path`;
- `save_dir`;
- `language`;
- `sample_rate`;
- `channels`;
- `auto_paste`;
- `save_audio`;
- `save_txt`;
- `always_on_top`.

Pendências:

- `config_version`;
- schema/validação;
- caminhos portáveis;
- `max_record_seconds`;
- `transcription_timeout_seconds`;
- aplicação real das flags de persistência;
- separar preferência local de configuração versionada.

Estado local conhecido do usuário:

`recording_mode = hold`, como alteração local ainda não commitada.

---

## 18. Inicialização

Entry point atual da `update`:

`ditado_f8_app.py`

Launcher silencioso:

`Iniciar Ditado F8 Widget.vbs`

O script da aplicação é resolvido relativamente ao VBS; o caminho do Python ainda é absoluto.

Launcher legado:

`Iniciar Ditado F8.bat -> ditado_f8.py`.

---

## 19. Estratégia de armazenamento

Atual:

- WAV/TXT em `save_dir`;
- timestamp `YYYYMMDD_HHMMSS`;
- histórico em memória;
- logs em `logs/ditado_f8.log`;
- logs rotativos;
- `*.log` ignorado pelo Git.

Pendências:

- flags `save_audio`/`save_txt` ainda não controlam a persistência;
- nomes podem colidir dentro do mesmo segundo;
- storage ainda não está isolado.

Não mover/apagar gravações existentes automaticamente.

---

## 20. Privacidade

Status atual:

- processamento local/offline;
- sem API de nuvem introduzida;
- sem telemetria;
- logging local;
- transcrição integral não registrada por padrão;
- teste do usuário confirmou que a frase completa de teste não apareceu no log;
- eventos registram metadados como `text_length`, estado, duração e nomes técnicos de arquivos.

Atenção: caminhos locais e nomes de arquivos podem aparecer nos logs técnicos.

---

## 21. Observabilidade

`IMPLEMENTADA PARCIALMENTE / TESTADA PELO USUÁRIO`.

Eventos atualmente observados/implementados incluem:

- `logging_configured`;
- `runtime_instrumentation_installed`;
- `application_start`;
- `application_controller_init`;
- `application_ready`;
- `config_loaded`;
- `microphone_detection_start`;
- `microphone_detection_success`;
- `hotkey_registering`;
- `hotkey_registered`;
- `event_published`;
- `event_dispatch`;
- `event_ignored`;
- `state_transition`;
- `recording_start_requested`;
- `recording_started`;
- `recording_stop_requested`;
- `recording_stopped`;
- `recording_cancel_requested`;
- `recording_cancelled`;
- `processing_started`;
- `processing_thread_enter`;
- `processing_thread_exit`;
- `wav_save_start/success/error`;
- `whisper_start`;
- `whisper_success`;
- `whisper_empty`;
- `whisper_error`;
- `txt_save_start/success/error`;
- `transcript_available`;
- `transcript_empty_display`;
- `history_item_added`;
- `output_copy`;
- `output_paste`;
- `output_copy_error`;
- `output_paste_error`;
- `ui_status_change`;
- `application_close_requested`;
- `application_shutdown_start`;
- `application_shutdown`;
- `application_mainloop_exit`;
- `unexpected_exception`.

Ainda não existem eventos reais para recursos ainda não implementados, como timeout e limite de gravação.

---

## 22. Roadmap

### M1

`CONCLUÍDO / TESTADO PELO USUÁRIO`.

### M2

`PARCIAL`.

Dispatcher/FSM de entrada implementados; toggle, hold, botão, Whisper real, output e fechamento normal passaram. Cancelamento e casos de shutdown concorrente ainda impedem conclusão formal.

### M3

`NÃO INICIADO`: `RecordingService` + `AudioDeviceService`.

### M4–M9

`NÃO INICIADOS`.

### M10 — LoggingService

`IMPLEMENTADO ANTECIPADAMENTE / PARCIALMENTE VALIDADO` por necessidade diagnóstica durante M2.

### M11–M14

`NÃO INICIADOS`.

---

## 23. Regras de Git

- `main` é referência e permanece sem commits deste trabalho;
- implementação somente em `update`;
- preferir fast-forward para sincronização local;
- nunca usar operações destrutivas sem autorização explícita;
- não usar `git add .` automaticamente;
- revisar diffs;
- não versionar logs, WAV, modelos ou transcrições privadas;
- preservar `config.json` local modificado enquanto sua intenção não for explicitamente revista.

---

## 24. Regras de trabalho para futuras IAs

1. Ler este handoff primeiro.
2. Revalidar branch/HEAD/diff antes de editar.
3. Não refazer trabalho já implementado.
4. Diferenciar `IMPLEMENTADO`, `VERIFICADO ESTATICAMENTE`, `TESTADO PELO USUÁRIO`, `NÃO TESTADO`, `BLOQUEADO`, `PARCIAL`.
5. Não declarar teste manual sem evidência do usuário.
6. Não descartar a alteração local conhecida em `config.json`.
7. Fornecer comandos PowerShell completos.
8. Manter commits pequenos e reversíveis.
9. Atualizar este handoff ao fim de marcos relevantes.
10. Não registrar texto integral do usuário em logs.
11. Não assumir que `Texto colado` prova foco seguro; F05 continua pendente.

---

## 25. Últimos comandos/operações executados

### GitHub

- comparação `main...update`;
- implementação de `LoggingService`;
- instrumentação do fluxo principal;
- instrumentação real de `pyperclip.copy` e `keyboard.press_and_release`;
- correção da semântica de log para transcrição vazia;
- atualização deste handoff.

### Local do usuário

Entre outros:

```powershell
git fetch origin
git merge --ff-only origin/update
git rev-parse HEAD
git status
git diff -- .\config.json
python -m py_compile .\logging_service.py .\ditado_f8_app.py .\ditado_f8_widget.py
python .\ditado_f8_app.py
Get-Content .\logs\ditado_f8.log -Encoding UTF8
```

Último HEAD local confirmado pelo usuário antes do commit `0278f2c`:

`19f69e5f92d76992a1219e0b7d05505cce53d1ed`.

Alteração local conhecida:

`config.json`: `recording_mode` de `toggle` para `hold`.

---

## 26. Próximo passo recomendado

Concluir M2 antes de iniciar M3.

Próximo teste isolado recomendado: **cancelamento por ESC em modo hold**.

Critérios:

1. F8 inicia uma gravação;
2. ESC durante `RECORDING` publica `CANCEL`;
3. estado passa por `CANCELLING`;
4. stream é encerrado;
5. frames são descartados;
6. Whisper não é iniciado para essa gravação;
7. app retorna a `IDLE/Pronto`;
8. manter F8 pressionado após ESC não deve iniciar nova gravação inesperadamente;
9. nenhuma exceção/traceback;
10. logs devem registrar cancelamento sem texto sensível.

Depois testar cancelamento pelo botão e idempotência relacionada.

---

## 27. Critério de conclusão do M1

`ATENDIDO`.

- branch correta;
- handoff criado;
- base confirmada;
- main intacta;
- sincronização segura validada.

---

## 28. Critério de conclusão do M2

M2 poderá ser marcado `CONCLUÍDO` somente após evidência suficiente de:

- boundary `keyboard -> dispatcher -> Tk` funcional;
- hold funcional;
- toggle funcional;
- botão funcional;
- cancelamento funcional;
- eventos incompatíveis/duplicados sem corromper estado;
- fechamento normal funcional;
- nenhum erro sintático/import;
- diff revisado;
- handoff atualizado.

Estado atual:

- hold: PASS;
- toggle: PASS;
- botão: PASS;
- output/Whisper: PASS;
- fechamento normal: PASS;
- parte da idempotência em `PROCESSING`: PASS;
- cancelamento: PENDENTE;
- shutdown concorrente: PENDENTE e tratado como estabilização crítica.

Shutdown durante processamento não deve ser confundido com fechamento normal em `IDLE`.
