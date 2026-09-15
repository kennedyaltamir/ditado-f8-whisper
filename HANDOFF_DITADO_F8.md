# HANDOFF_DITADO_F8.md

> Projeto: Ditado F8 Whisper  
> Repositório: `kennedyaltamir/ditado-f8-whisper`  
> Branch de trabalho: `update`  
> Branch base: `main`  
> SHA-base de `main`: `c65fe91b60f2142afa3338f20874535610562e11`  
> Último commit funcional/documental antes desta atualização: `261bcb2e124c12cd841bf2e09489ef2a74e39821`  
> Data do marco: 2026-09-15

---

## 1. Identificação do projeto

Aplicação desktop local para Windows 11, escrita em Python, destinada a capturar áudio por hotkey/botão, transcrever localmente com `whisper.cpp` (`whisper-cli.exe`) e copiar/colar o texto no aplicativo de destino.

Fluxo funcional principal a preservar:

`F8 -> gravação -> Whisper local -> texto -> clipboard/colagem`

Comportamentos que devem permanecer disponíveis:

- modo hold;
- modo toggle;
- botão visual;
- cancelamento;
- histórico;
- configuração;
- inicialização silenciosa;
- persistência WAV/TXT conforme configuração;
- operação local/offline.

---

## 2. Estado da branch

### Remoto — VERIFICADO

- `main`: `c65fe91b60f2142afa3338f20874535610562e11`;
- `update`: `261bcb2e124c12cd841bf2e09489ef2a74e39821` antes deste commit documental;
- `update` está 4 commits à frente e 0 atrás de `main` nesse ponto;
- merge-base é o próprio `c65fe91b60f2142afa3338f20874535610562e11`;
- `main` não foi alterada durante o trabalho.

### Local do usuário — TESTADO PELO USUÁRIO

Após `git fetch` e `git merge --ff-only origin/update`:

- branch local: `update`;
- HEAD local: `261bcb2e124c12cd841bf2e09489ef2a74e39821`;
- `origin/update` alinhado ao mesmo SHA;
- working tree: limpo.

Esse estado deve ser atualizado por fast-forward após novos commits remotos antes dos próximos testes.

---

## 3. Último commit validado

Último commit de código/launcher testado estaticamente e sincronizado localmente:

`261bcb2e124c12cd841bf2e09489ef2a74e39821` — `fix: iniciar app a partir do diretorio do launcher`

Commits da `update` até esse ponto:

1. `f73fc9d99923fc7604eee00e009ca45c11fe4bd3` — `docs: criar handoff tecnico inicial da branch update`;
2. `618badb6744f411d33e01ded21991ee474383ee0` — `refactor: adicionar dispatcher de eventos e estado inicial`;
3. `bdf49166b834f01c47e92c525a90e2e9420fb4c8` — `refactor: iniciar widget pelo dispatcher de eventos`;
4. `261bcb2e124c12cd841bf2e09489ef2a74e39821` — `fix: iniciar app a partir do diretorio do launcher`.

O SHA deste commit documental deve ser registrado na próxima atualização do handoff.

---

## 4. Objetivo do projeto

Evoluir o MVP funcional para uma aplicação desktop local robusta, determinística, testável, diagnosticável e preparada para futura distribuição sem regressão do fluxo existente.

A evolução deve permanecer incremental, verificável e reversível.

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

M2 introduziu um entrypoint/controlador transitório em `ditado_f8_app.py`.

Esse módulo adiciona:

- `AppState`;
- `AppEvent`;
- `queue.SimpleQueue` para eventos;
- publicação de eventos pelo callback global do `keyboard`;
- drenagem da fila pelo loop Tk via `root.after`;
- despacho central de eventos de entrada;
- bloqueio de novos eventos depois do início do fechamento;
- estados transitórios `IDLE`, `RECORDING`, `PROCESSING`, `CANCELLING`, `ERROR`, `SHUTTING_DOWN`, `CLOSED`.

A arquitetura ainda é transitória: gravação, processamento e shutdown real continuam delegados ao `DitadoWidget` legado.

Arquivos principais:

- `ditado_f8_app.py` — entrypoint atual da refatoração/event dispatcher;
- `ditado_f8_widget.py` — implementação funcional monolítica ainda reutilizada;
- `config.json` — configuração ativa;
- `Iniciar Ditado F8 Widget.vbs` — launcher silencioso apontando para `ditado_f8_app.py` relativo à pasta do próprio VBS;
- `Iniciar Ditado F8.bat` — launcher legado para `ditado_f8.py`;
- `ditado_f8.py` — implementação legada;
- `ditado_f8_widget_backup_controle.py` — backup versionado;
- documentação em `docs/`;
- `PROXIMAS_FASES_DITADO_F8.md`;
- `ROADMAP_FEATURES_DITADO_F8.md`.

---

## 6. Arquitetura alvo

Separação incremental, sem reescrita total:

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

Fluxo alvo:

`UI -> Event Dispatch -> AppController -> RecordingService -> WhisperService -> StorageService -> OutputController -> UI`

---

## 7. Fluxo operacional

### Hold

Alvo atual de M2:

`HOTKEY_DOWN -> dispatcher -> iniciar gravação -> HOTKEY_UP -> dispatcher -> parar/processar`

Status: `IMPLEMENTADO`, porém `NÃO TESTADO` manualmente após M2.

### Toggle

Alvo atual de M2:

`HOTKEY_DOWN -> dispatcher -> iniciar -> novo HOTKEY_DOWN -> dispatcher -> parar/processar`

Status: `IMPLEMENTADO`, porém `NÃO TESTADO` manualmente após M2.

### Botão

`BUTTON_START/BUTTON_STOP -> dispatcher -> gravação/processamento`

Status: `IMPLEMENTADO`, porém `NÃO TESTADO` manualmente após M2.

### Cancelamento

`CANCEL -> dispatcher -> CANCELLING -> cancelamento legado -> IDLE`

Status: `IMPLEMENTADO`, porém `NÃO TESTADO` manualmente após M2.

### Fechamento normal

`APPLICATION_CLOSE -> SHUTTING_DOWN -> fechamento legado -> CLOSED`

Status: `TESTADO PELO USUÁRIO` para fechamento normal pelo botão `X` quando o app não estava em processamento.

---

## 8. Máquina de estados

Estados definidos em `ditado_f8_app.py`:

- `IDLE`;
- `RECORDING`;
- `PROCESSING`;
- `CANCELLING`;
- `ERROR`;
- `SHUTTING_DOWN`;
- `CLOSED`.

Eventos atualmente definidos:

- `HOTKEY_DOWN`;
- `HOTKEY_UP`;
- `BUTTON_START`;
- `BUTTON_STOP`;
- `CANCEL`;
- `APPLICATION_CLOSE`.

Eventos ainda não modelados no dispatcher:

- `RECORD_LIMIT_REACHED`;
- `RECORDING_ERROR`;
- `TRANSCRIPTION_SUCCESS`;
- `TRANSCRIPTION_EMPTY`;
- `TRANSCRIPTION_ERROR`;
- `TRANSCRIPTION_TIMEOUT`.

Classificação: `PARCIAL`.

A FSM ainda espelha `self.is_processing` do widget legado para retornar de `PROCESSING` a `IDLE`; isso deve desaparecer quando resultados de transcrição forem estruturados e publicados como eventos explícitos.

---

## 9. Componentes principais

### `ditado_f8_app.py`

Controlador transitório/event dispatcher. É o entrypoint atual da branch `update`.

### `ditado_f8_widget.py`

Implementação funcional herdada pelo controlador transitório. Continua responsável pelas operações concretas de áudio, Whisper, persistência, UI e output.

### `config.json`

Configuração ativa. Ainda contém caminhos específicos do ambiente e flags de persistência não respeitadas pelo fluxo.

### `Iniciar Ditado F8 Widget.vbs`

Launcher silencioso. Agora resolve `ditado_f8_app.py` pela pasta do próprio VBS. O caminho do interpretador Python ainda é absoluto e específico do ambiente.

### `Iniciar Ditado F8.bat`

Launcher legado que ainda executa `ditado_f8.py` e depende de `C:\whispercpp`.

---

## 10. Problemas conhecidos

### F01 — CRITICAL — fronteira `keyboard -> Tkinter`

**PARCIALMENTE CORRIGIDO EM M2.** No entrypoint atual `ditado_f8_app.py`, o callback global não chama diretamente métodos Tk/gravação; ele publica eventos para a fila. O dispatcher executado via Tk processa esses eventos.

Pendência: callbacks do Whisper/thread de processamento e demais caminhos assíncronos ainda dependem do widget legado e precisam de revisão própria.

### F02 — HIGH — sem limite máximo de gravação

**PENDENTE.** Não há `max_record_seconds`.

### F03 — HIGH — caminhos específicos de ambiente

**PENDENTE.** Config/defaults ainda dependem de `C:\whispercpp\...`.

### F04 — HIGH — launcher VBS não portátil

**PARCIALMENTE CORRIGIDO.** O caminho do script passou a ser relativo ao VBS. O caminho do Python ainda é absoluto.

### F05 — HIGH — foco da janela de destino

**PENDENTE.** `Ctrl+V` ainda pode ser enviado sem restauração segura da janela-alvo.

### F06 — HIGH — resultado Whisper sem semântica estruturada

**PENDENTE.** `transcribe_wav()` ainda retorna `str`.

### F07 — MEDIUM — parser Whisper acoplado

**PENDENTE.** Parsing continua dentro do fluxo legado.

### F08 — MEDIUM — possível colisão de nomes

**PENDENTE.** Timestamp continua com resolução de segundos.

### F09 — MEDIUM — microfone resolvido apenas no início

**PENDENTE.** Sem recuperação/re-enumeração ativa.

### F10 — MEDIUM — status do callback de áudio ignorado

**PENDENTE.** O parâmetro `status` ainda não é tratado.

### F11 — MEDIUM — estado compartilhado baseado em booleanos

**PARCIALMENTE CORRIGIDO.** Existe `AppState`, mas o controlador ainda espelha `is_recording`/`is_processing` do widget legado. A migração para FSM como única fonte de estado ainda não terminou.

### F12 — MEDIUM — shutdown não coordenado

**PENDENTE.** Fechamento normal foi testado, mas fechamento durante `RECORDING`/`PROCESSING` e callbacks tardios continuam sem validação/coordenação completa.

### F13 — MEDIUM — Whisper sem timeout

**PENDENTE.** `subprocess.run()` continua sem timeout.

### F14 — MEDIUM — configuração sem schema/versionamento

**PENDENTE.** Sem `config_version` e sem validador formal.

### F15 — MEDIUM — dependências não formalizadas

**PENDENTE.** Nenhum `requirements.txt`/`pyproject.toml` foi introduzido até M2.

### F16 — MEDIUM — testes automatizados ausentes

**PENDENTE.** Nenhuma suíte automatizada foi adicionada até M2.

### F17 — MEDIUM — logging estruturado ausente

**PENDENTE.**

### F18/F25 — HIGH — flags de persistência não controlam persistência

**PENDENTE.** `save_audio` e `save_txt` existem, mas o fluxo legado salva WAV/TXT incondicionalmente.

### F19 — MEDIUM — histórico baseado em dicionários

**PENDENTE.** Sem `DictationRecord`.

### F20 — LOW — backup versionado

**PENDENTE DE REVISÃO.** Não remover antes da política de legacy.

### F21 — LOW — implementação legada paralela

**PENDENTE DE REVISÃO.** `ditado_f8.py` ainda é referenciado pelo BAT.

### F22 — LOW — `keyboard.unhook_all()`

**PENDENTE.** O widget legado continua removendo todos os hooks do módulo/processo.

### F23 — LOW — conversão de áudio sem clamp

**PENDENTE.** `np.int16(audio_data * 32767)` continua sem `np.clip`.

### F24 — ARCHITECTURAL — `process_audio()` concentra responsabilidades

**PENDENTE.**

### F26 — MEDIUM — idempotência dos eventos

**PARCIALMENTE IMPLEMENTADO / NÃO TESTADO SUFICIENTEMENTE.**

O dispatcher ignora eventos incompatíveis com vários estados, e o latch evita múltiplos `HOTKEY_DOWN` durante a mesma pressão física. Ainda devem ser testados explicitamente:

- `HOTKEY_DOWN` duplicado;
- `HOTKEY_UP` sem gravação;
- `CANCEL` duplicado;
- `STOP` após `CANCEL`;
- `APPLICATION_CLOSE` durante `RECORDING`;
- `APPLICATION_CLOSE` durante `PROCESSING`;
- evento/resultado tardio depois de `SHUTTING_DOWN`/`CLOSED`.

---

## 11. Problemas críticos

Prioridade operacional atual:

1. concluir validação de M2 — dispatcher/FSM de entrada;
2. coordenar shutdown e callbacks tardios;
3. isolar RecordingService/AudioDeviceService;
4. estruturar Whisper e resultados;
5. timeout/classificação de falhas;
6. limite máximo de gravação;
7. recuperação de microfone/status de áudio;
8. OutputController/foco seguro;
9. persistência coerente com `save_audio`/`save_txt`;
10. configuração/versionamento, logging, dependências e testes.

---

## 12. Melhorias implementadas

### M1 — CONCLUÍDO

- branch `update` derivada de `main` correto;
- handoff criado;
- base e diff verificados;
- sincronização local por fast-forward validada.

### M2 — PARCIAL

Implementado:

- `ditado_f8_app.py`;
- `AppState`;
- `AppEvent`;
- fila thread-safe;
- event dispatch pelo loop Tk;
- hotkey global apenas publica eventos;
- botões/start/stop/cancel/close entram no dispatcher;
- launcher VBS usa novo entrypoint;
- launcher resolve o script pela própria pasta.

Ainda não considerado concluído por falta dos testes funcionais restantes.

---

## 13. Melhorias pendentes

### Para concluir M2

- testar modo toggle;
- testar modo hold;
- testar botão visual;
- testar cancelamento;
- testar idempotência básica;
- analisar fechamento durante gravação/processamento antes de considerar shutdown seguro;
- atualizar este handoff com resultados finais.

### M3+

Não iniciar antes da conclusão/aceite de M2, salvo correção estritamente necessária de regressão descoberta durante seus testes.

---

## 14. Testes executados

### VERIFICADO ESTATICAMENTE — IA/GitHub

- branch `update` e relação com `main`;
- diff restrito aos arquivos esperados;
- revisão de `ditado_f8_app.py`;
- revisão dos launchers e código legado relevante.

### TESTADO PELO USUÁRIO — Windows 11 / Python 3.10.6

Comandos executados:

```powershell
python --version
python -m py_compile .\ditado_f8_widget.py .\ditado_f8_app.py
python -c "import ditado_f8_app; print('IMPORT_OK')"
```

Resultados:

- Python `3.10.6`;
- `py_compile`: PASS, sem erro reportado;
- import: `IMPORT_OK`;
- abertura com `python .\ditado_f8_app.py`: PASS;
- fechamento normal clicando no `X`: PASS;
- retorno ao prompt sem traceback no fechamento pelo `X`: PASS;
- `git status` após os testes: working tree limpo.

Um encerramento anterior por `Ctrl+C` gerou `KeyboardInterrupt`; não foi classificado como falha do aplicativo porque o teste correto pelo `X` foi repetido e passou.

---

## 15. Testes não executados

**NÃO TESTADO após M2:**

- F8 hold;
- F8 toggle;
- botão visual;
- cancelamento;
- duplicidade/idempotência de eventos;
- microfone real no novo fluxo;
- Whisper real no novo fluxo;
- clipboard/auto-paste no novo fluxo;
- restauração de foco;
- fechamento durante `RECORDING`;
- fechamento durante `PROCESSING`;
- callback/resultado tardio após shutdown;
- timeout;
- limite de gravação;
- erros de executável/modelo;
- testes automatizados.

---

## 16. Dependências

Imports externos confirmados no núcleo/refatoração:

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
- `winsound`.

Whisper permanece dependência externa local: `whisper-cli.exe` + modelo GGML.

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

Pendências: `config_version`, schema/validação, caminhos portáveis, `max_record_seconds`, `transcription_timeout_seconds` e aplicação real das flags de persistência.

---

## 18. Inicialização

Entry point atual da `update`:

`ditado_f8_app.py`

Launcher silencioso:

`Iniciar Ditado F8 Widget.vbs`

O VBS resolve o script em relação à própria pasta, mas o Python ainda está em caminho absoluto específico do ambiente.

Launcher alternativo/legado:

`Iniciar Ditado F8.bat` -> `ditado_f8.py`.

---

## 19. Estratégia de armazenamento

Atual, herdada do monólito:

- WAV/TXT em `save_dir`;
- timestamp `YYYYMMDD_HHMMSS`;
- histórico somente em memória;
- persistência WAV/TXT ainda ocorre mesmo quando flags deveriam desabilitá-la.

Não mover ou apagar gravações existentes durante a refatoração.

---

## 20. Privacidade

- processamento local/offline;
- nenhuma telemetria introduzida em M1/M2;
- nenhum upload de áudio/texto introduzido;
- logs estruturados ainda não existem;
- quando forem implementados, não devem registrar texto integral por padrão;
- gravações/transcrições/modelos não devem ser adicionados ao Git.

---

## 21. Observabilidade

Ainda não implementada formalmente.

Eventos futuros mínimos:

`application_start`, `application_shutdown`, `config_load`, `config_error`, `microphone_detection`, `recording_start`, `recording_stop`, `recording_cancel`, `recording_error`, `recording_limit_reached`, `whisper_start`, `whisper_success`, `whisper_empty`, `whisper_error`, `whisper_timeout`, `output_copy`, `output_paste`, `unexpected_exception`.

---

## 22. Roadmap

### M1

`CONCLUÍDO / TESTADO PELO USUÁRIO`.

### M2

`PARCIAL`: dispatcher e FSM de entrada implementados, validação estática e teste de start/close concluídos; fluxo funcional de gravação ainda precisa de teste.

### M3

`NÃO INICIADO`: isolar `RecordingService` e `AudioDeviceService`.

### M4+

`NÃO INICIADOS`.

Divergência documental histórica: documentos anteriores afirmaram thread safety completa; isso não deve ser considerado verdadeiro até que todos os caminhos assíncronos relevantes sejam auditados/validados.

---

## 23. Regras de Git

- `main` é referência e não deve receber commits deste trabalho;
- implementação somente em `update`;
- atualizar localmente por operações seguras/fast-forward quando aplicável;
- revisar diff antes de commits;
- não usar `git reset --hard`, `git clean -fd`, `git clean -fdx`, `git checkout -- .`, `git restore .` ou `push --force` sem autorização;
- não usar `git add .` automaticamente;
- não versionar modelos, gravações, transcrições ou arquivos sensíveis.

---

## 24. Regras de trabalho para futuras IAs

1. Ler este handoff.
2. Confirmar `main`, `update`, HEAD e diff real.
3. Não refazer milestones implementados.
4. Diferenciar `IMPLEMENTADO`, `VERIFICADO ESTATICAMENTE`, `TESTADO PELO USUÁRIO`, `NÃO TESTADO`, `BLOQUEADO`, `PARCIAL`.
5. Não avançar estruturalmente enquanto o milestone anterior tiver regressão não analisada.
6. Fornecer comandos PowerShell completos para validações locais.
7. Não declarar teste manual executado sem saída do usuário.
8. Atualizar este handoff ao fim dos marcos e quando o estado registrado ficar materialmente desatualizado.
9. Informar SHAs completos.
10. Preservar comportamento funcional e privacidade.

---

## 25. Últimos comandos/operações executados

### GitHub

- comparação `main...update`;
- confirmação de `main = c65fe91b60f2142afa3338f20874535610562e11`;
- confirmação de `update = 261bcb2e124c12cd841bf2e09489ef2a74e39821` antes deste commit;
- leitura de `ditado_f8_app.py`;
- atualização deste handoff para refletir M2 parcial.

### Local do usuário

```powershell
git fetch origin
git merge --ff-only origin/update
git status
git rev-parse HEAD
git log --oneline --decorate -n 5
python --version
python -m py_compile .\ditado_f8_widget.py .\ditado_f8_app.py
python -c "import ditado_f8_app; print('IMPORT_OK')"
python .\ditado_f8_app.py
git status
```

Último estado local confirmado antes deste commit documental: `261bcb2e124c12cd841bf2e09489ef2a74e39821`, working tree limpo.

---

## 26. Próximo passo recomendado

Concluir M2 antes de M3.

Próximo teste isolado: **modo toggle**, pois `config.json` estava configurado com `recording_mode = toggle` na auditoria.

Critérios mínimos do teste:

1. primeiro F8 inicia uma única gravação;
2. segundo F8 encerra a mesma gravação;
3. Whisper processa;
4. texto reconhecido é disponibilizado;
5. app retorna a estado pronto;
6. nenhuma segunda gravação concorrente é iniciada;
7. sem traceback no terminal.

A colagem automática deve ser observada, mas falha de foco deve ser registrada separadamente de falha do dispatcher, pois F05 ainda está pendente.

Após toggle, testar isoladamente hold, botão, cancelamento e idempotência básica antes de concluir M2.

---

## 27. Critério de conclusão do M1

**ATENDIDO.**

- branch `update` criada do `main` correto;
- handoff presente;
- commit documental exclusivo criado;
- `main` inalterada;
- SHA validado;
- sincronização local por fast-forward confirmada.

---

## 28. Critério de conclusão do M2

M2 só poderá ser marcado `CONCLUÍDO` quando houver evidência suficiente de:

- boundary `keyboard -> dispatcher -> Tk` funcionando;
- hold funcionando;
- toggle funcionando;
- botão visual funcionando;
- cancelamento funcionando;
- fechamento normal funcionando;
- eventos incompatíveis/duplicados não corrompendo estado;
- nenhum erro sintático/import;
- diff revisado;
- handoff atualizado com resultados reais.

Shutdown durante processamento não deve ser confundido com o fechamento normal já testado; a coordenação completa continua como trabalho de estabilização e deve ser tratada antes de se declarar shutdown robusto.
