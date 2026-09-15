# HANDOFF_DITADO_F8.md

> Projeto: Ditado F8 Whisper  
> Repositório: `kennedyaltamir/ditado-f8-whisper`  
> Branch de trabalho: `update`  
> Branch base: `main`  
> SHA-base validado: `c65fe91b60f2142afa3338f20874535610562e11`  
> Data do marco: 2026-09-15

---

## 1. Identificação do projeto

Aplicação desktop local para Windows 11, escrita em Python, destinada a capturar áudio por hotkey/botão, transcrever localmente com `whisper.cpp` (`whisper-cli.exe`) e copiar/colar o texto no aplicativo de destino.

Fluxo funcional principal a preservar:

`segurar F8 -> falar -> soltar F8 -> transcrever -> copiar/colar`

Também devem ser preservados: modo hold, modo toggle, botão visual, cancelamento, histórico, configuração, inicialização silenciosa, salvamento WAV/TXT e operação local/offline.

---

## 2. Estado da branch

- `main` remoto auditado em `c65fe91b60f2142afa3338f20874535610562e11`.
- A branch remota `update` foi criada a partir exatamente desse SHA.
- Nenhuma alteração foi feita em `main` neste marco.
- Existe também uma branch experimental anterior `ai/update`; ela não é a branch operacional definida por este handoff.
- Estado local informado anteriormente pelo usuário: branch local `update`, working tree limpo, HEAD alinhado ao mesmo SHA-base. Esse estado local deve ser revalidado pelo usuário antes de testes locais futuros.

---

## 3. Último commit validado

Base validada antes deste documento:

`c65fe91b60f2142afa3338f20874535610562e11` — `docs: registrar proximas fases do ditado f8`

Este documento será o primeiro commit exclusivo da branch `update`.

---

## 4. Objetivo do projeto

Evoluir o MVP funcional para uma aplicação desktop local robusta, determinística, testável, diagnosticável, portátil entre instalações Windows e preparada para futura distribuição, sem regressão do fluxo funcional existente.

A evolução deve ser incremental, verificável e reversível.

---

## 5. Arquitetura atual

O núcleo permanece concentrado em `ditado_f8_widget.py`, que reúne:

- UI Tkinter;
- configuração;
- hotkeys globais via `keyboard`;
- captura de áudio via `sounddevice`;
- seleção de dispositivo;
- estado operacional;
- armazenamento WAV/TXT;
- execução do Whisper;
- parsing da saída;
- histórico em memória;
- clipboard;
- simulação de `Ctrl+V`;
- shutdown.

Arquivos relevantes confirmados:

- `ditado_f8_widget.py`;
- `ditado_f8.py`;
- `ditado_f8_widget_backup_controle.py`;
- `config.json`;
- `Iniciar Ditado F8 Widget.vbs`;
- `Iniciar Ditado F8.bat`;
- `README.md`;
- documentação em `docs/`;
- `PROXIMAS_FASES_DITADO_F8.md`;
- `ROADMAP_FEATURES_DITADO_F8.md`.

---

## 6. Arquitetura alvo

Separação incremental, sem reescrita total, em componentes conceituais:

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

`HOTKEY_DOWN -> iniciar gravação -> HOTKEY_UP -> parar -> processar -> transcrever -> salvar -> copiar/colar`

### Toggle

`HOTKEY_DOWN -> iniciar gravação -> HOTKEY_DOWN seguinte -> parar -> processar -> transcrever -> salvar -> copiar/colar`

### Botão

`BUTTON_START -> iniciar -> BUTTON_STOP -> processar -> transcrever -> salvar -> copiar/colar`

### Cancelamento

`CANCEL -> parar stream -> descartar frames atuais -> não chamar Whisper`

Estado atual: o código ainda depende de múltiplos booleanos e chamadas diretas; não existe dispatcher central nem máquina de estados explícita.

---

## 8. Máquina de estados

Estados-alvo:

- `IDLE`;
- `RECORDING`;
- `PROCESSING`;
- `CANCELLING`;
- `ERROR`;
- `SHUTTING_DOWN`;
- `CLOSED`.

Eventos-alvo:

- `HOTKEY_DOWN`;
- `HOTKEY_UP`;
- `BUTTON_START`;
- `BUTTON_STOP`;
- `CANCEL`;
- `APPLICATION_CLOSE`;
- `RECORD_LIMIT_REACHED`;
- `RECORDING_ERROR`;
- `TRANSCRIPTION_SUCCESS`;
- `TRANSCRIPTION_EMPTY`;
- `TRANSCRIPTION_ERROR`;
- `TRANSCRIPTION_TIMEOUT`.

Ainda não implementada neste marco.

---

## 9. Componentes principais

### `ditado_f8_widget.py`
Entrypoint atual do widget e núcleo funcional.

### `config.json`
Configuração ativa. Atualmente contém caminhos absolutos de ambiente e flags `save_audio`/`save_txt`.

### `Iniciar Ditado F8 Widget.vbs`
Launcher silencioso. Atualmente referencia caminho absoluto do Python e do script.

### `Iniciar Ditado F8.bat`
Launcher alternativo; ainda executa `ditado_f8.py` e usa `C:\whispercpp`.

### `ditado_f8.py`
Código legado ainda referenciado pelo BAT; não remover sem análise separada.

### `ditado_f8_widget_backup_controle.py`
Backup versionado; não remover sem busca de referências e commit próprio.

---

## 10. Problemas conhecidos

### F01 — CRITICAL — fronteira `keyboard -> Tkinter`
**CONFIRMADO.** `keyboard.hook(self.on_key_event)` conduz a chamadas diretas de `start_recording()`, `stop_and_process()` e `cancel_recording()`. Esses caminhos chegam a operações Tk como `btn.config`, `after_cancel` e escrita em `StringVar`. Nem toda alteração visual é despachada para o loop principal.

### F02 — HIGH — sem limite máximo de gravação
**CONFIRMADO.** Frames são acumulados enquanto `is_recording` for verdadeiro; não existe `max_record_seconds`.

### F03 — HIGH — caminhos específicos de ambiente
**CONFIRMADO.** `config.json` e defaults usam `C:\whispercpp\...`.

### F04 — HIGH — launcher VBS não portátil
**CONFIRMADO.** Usa caminho absoluto para Python do perfil Windows e para o script.

### F05 — HIGH — foco da janela de destino
**CONFIRMADO COMO RISCO.** O código envia `keyboard.press_and_release("ctrl+v")` sem capturar/validar/restaurar explicitamente a janela-alvo.

### F06 — HIGH — resultado Whisper sem semântica estruturada
**CONFIRMADO.** `transcribe_wav()` retorna apenas `str`.

### F07 — MEDIUM — parser Whisper acoplado
**CONFIRMADO.** Regex de parsing está dentro de `transcribe_wav()`.

### F08 — MEDIUM — possível colisão de nomes
**CONFIRMADO.** `process_audio()` usa timestamp com resolução de segundos.

### F09 — MEDIUM — microfone resolvido apenas no início
**CONFIRMADO.** `device_index` é resolvido no `__init__` e não há recuperação ativa antes de nova sessão.

### F10 — MEDIUM — `status` do callback de áudio ignorado
**CONFIRMADO.** O callback recebe `status`, mas não o trata.

### F11 — MEDIUM — estado distribuído em booleanos
**CONFIRMADO.** `is_recording`, `is_processing`, `is_hotkey_pressed`, `cancel_until_hotkey_released`, `frames` e `stream` coordenam o estado sem FSM explícita.

### F12 — MEDIUM — shutdown não coordenado
**CONFIRMADO.** `on_close()` fecha stream, desregistra hooks e destrói a root, sem coordenação explícita com thread/subprocesso em andamento.

### F13 — MEDIUM — Whisper sem timeout
**CONFIRMADO.** `subprocess.run(...)` não recebe `timeout=`.

### F14 — MEDIUM — configuração sem schema/versionamento
**CONFIRMADO.** Não há `config_version` nem validação formal.

### F15 — MEDIUM — dependências não formalizadas
**CONFIRMADO NA AUDITORIA ANTERIOR.** Não foi identificado `requirements.txt` ou `pyproject.toml` no tree auditado.

### F16 — MEDIUM — ausência de testes automatizados
**CONFIRMADO NA AUDITORIA ANTERIOR.** Não foi identificada suíte automatizada.

### F17 — MEDIUM — sem logging estruturado
**CONFIRMADO.** Não existe infraestrutura formal de logging técnico no módulo principal.

### F18 — MEDIUM — persistência/privacidade não formalizadas
**CONFIRMADO.** As flags `save_audio` e `save_txt` existem na configuração, porém `process_audio()` chama `save_wav()` e `save_txt()` incondicionalmente.

### F19 — MEDIUM — histórico baseado em dicionários
**CONFIRMADO.** `history_items` contém dicionários; não há `DictationRecord`.

### F20 — LOW — backup versionado
**CONFIRMADO.** `ditado_f8_widget_backup_controle.py` permanece versionado.

### F21 — LOW — implementação legada paralela
**CONFIRMADO.** `ditado_f8.py` ainda é chamado por `Iniciar Ditado F8.bat`.

### F22 — LOW — `keyboard.unhook_all()`
**CONFIRMADO.** `unregister_hotkeys()` remove todos os hooks do módulo/processo em vez de uma referência própria.

### F23 — LOW — conversão de áudio sem clamp
**CONFIRMADO.** `save_wav()` converte com `np.int16(audio_data * 32767)` sem `np.clip`.

### F24 — ARCHITECTURAL — `process_audio()` concentra responsabilidades
**CONFIRMADO.** Persistência, transcrição, parsing, histórico, clipboard, paste, status e erro continuam acoplados.

### F25 — HIGH — flags de persistência não controlam persistência
**CONFIRMADO.** `save_audio`/`save_txt` estão no config, mas não impedem criação dos arquivos.

### F26 — MEDIUM — idempotência dos eventos
**PENDENTE DE IMPLEMENTAÇÃO/TESTE.** Devem ser tratados explicitamente: `HOTKEY_DOWN` duplicado, `HOTKEY_UP` sem gravação, `CANCEL` duplicado, `STOP` após `CANCEL`, `CLOSE` durante `RECORDING`/`PROCESSING` e resultado tardio após shutdown.

---

## 11. Problemas críticos

Ordem operacional:

1. corrigir fronteira `keyboard -> Tkinter`;
2. criar event dispatch mínimo;
3. introduzir máquina de estados;
4. coordenar shutdown;
5. implementar timeout/classificação do Whisper;
6. implementar limite de gravação;
7. recuperação do microfone;
8. foco seguro da janela de destino;
9. persistência coerente com `save_audio`/`save_txt`.

---

## 12. Melhorias implementadas

Neste marco: somente infraestrutura Git e documentação inicial da branch `update`.

Nenhuma alteração funcional foi feita no aplicativo.

---

## 13. Melhorias pendentes

### Fase A — Estabilização
Thread safety, dispatcher, FSM, shutdown, timeout, semântica de falhas, limite de gravação, status de áudio, recuperação de dispositivo, foco/output e persistência coerente.

### Fase B — Fundação
ConfigService, `config_version`, parser isolado, identificadores únicos, `DictationRecord`, StorageService, OutputController, logging, dependências e testes.

### Fases C/D/E
Produto, distribuição e recursos avançados somente depois da estabilização.

---

## 14. Testes executados

### VERIFICADO REMOTAMENTE

- metadata do repositório;
- SHA atual de `main`;
- criação da branch `update` a partir do SHA-base;
- leitura do código principal;
- leitura de `config.json`;
- leitura dos launchers VBS/BAT;
- revalidação estática dos achados prioritários F01, F02, F03, F04, F05, F06, F07, F08, F09, F10, F11, F12, F13, F18/F25, F21, F22, F23 e F24.

Nenhum teste funcional local foi executado pela IA.

---

## 15. Testes não executados

**NÃO EXECUTADO:**

- `python -m py_compile` no checkout Windows do usuário;
- execução do aplicativo;
- F8 hold;
- F8 toggle;
- botão visual;
- cancelamento;
- microfone real;
- Whisper real;
- clipboard/auto-paste;
- foco/restauração;
- shutdown durante processing;
- timeout;
- limite de gravação;
- testes automatizados.

---

## 16. Dependências

Imports externos confirmados no núcleo:

- `keyboard`;
- `numpy`;
- `pyperclip`;
- `sounddevice`.

Dependências Windows/Python padrão incluem Tkinter, `winsound`, `wave`, `subprocess` e `threading`.

Whisper é dependência externa local: `whisper-cli.exe` + modelo GGML.

---

## 17. Configuração

`config.json` contém atualmente:

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

Problemas: sem `config_version`, sem schema, caminhos absolutos e flags de persistência sem efeito real no fluxo atual.

---

## 18. Inicialização

Principal: `Iniciar Ditado F8 Widget.vbs`.

Alternativo/legado: `Iniciar Ditado F8.bat` -> `ditado_f8.py`.

Ambos dependem atualmente de caminhos absolutos.

---

## 19. Estratégia de armazenamento

Atual:

- WAV e TXT em `save_dir`;
- base `YYYYMMDD_HHMMSS`;
- histórico somente em memória;
- fluxo salva WAV/TXT sempre, independentemente das flags de configuração.

Não mover/apagar arquivos existentes automaticamente durante a refatoração.

---

## 20. Privacidade

- processamento local/offline;
- sem API de nuvem observada;
- sem telemetria observada;
- futuros logs não devem gravar texto integral por padrão;
- persistência deve respeitar de fato `save_audio` e `save_txt`.

---

## 21. Observabilidade

Ainda não implementada formalmente.

Eventos futuros mínimos: `application_start`, `application_shutdown`, `config_load`, `config_error`, `microphone_detection`, `recording_start`, `recording_stop`, `recording_cancel`, `recording_error`, `recording_limit_reached`, `whisper_start`, `whisper_success`, `whisper_empty`, `whisper_error`, `whisper_timeout`, `output_copy`, `output_paste`, `unexpected_exception`.

---

## 22. Roadmap

Prioridade atual: estabilização antes de features cosméticas, histórico persistente avançado, tray ou distribuição.

Divergência documental já confirmada: `PROXIMAS_FASES_DITADO_F8.md` declara thread safety completa da UI, porém o hotkey global ainda aciona métodos que executam operações Tk diretamente.

---

## 23. Regras de Git

- `main` é referência; não desenvolver diretamente nele;
- implementação somente em `update`;
- revisar diff antes de stage/commit;
- não usar operações destrutivas sem autorização;
- não usar `git add .` automaticamente;
- um marco por commit lógico;
- não commitar modelos, gravações, transcrições ou artefatos sensíveis.

---

## 24. Regras de trabalho para futuras IAs

1. Ler este handoff primeiro.
2. Confirmar branch/HEAD/diff antes de alterar código.
3. Confrontar documentação com implementação real.
4. Não declarar teste executado sem evidência.
5. Diferenciar IMPLEMENTADO, VERIFICADO ESTATICAMENTE, TESTADO PELO USUÁRIO, NÃO TESTADO e BLOQUEADO.
6. Refatorar incrementalmente.
7. Não remover legacy/backup sem verificação.
8. Atualizar este documento após cada marco arquitetural.
9. Informar SHA do último commit confirmado.

---

## 25. Últimos comandos/operações executados

No GitHub remoto:

- leitura do metadata do repositório;
- leitura do HEAD de `main`;
- criação da branch `update` no SHA `c65fe91b60f2142afa3338f20874535610562e11`;
- leitura de `ditado_f8_widget.py`;
- leitura de `config.json`;
- leitura dos launchers VBS/BAT;
- criação deste documento.

No computador local do usuário nesta etapa: nenhum novo comando executado pela IA.

---

## 26. Próximo passo recomendado

M2: corrigir a fronteira `keyboard -> Tkinter` e introduzir event dispatch mínimo, preservando comportamento observável.

Antes do commit funcional de M2:

- revisar diff;
- validar sintaxe/imports;
- atualizar este handoff;
- solicitar testes manuais locais de hold, toggle, botão e cancelamento.

---

## 27. Critério de conclusão do M1

M1 está concluído somente quando houver evidência de:

- branch remota `update` criada a partir do `main` correto;
- `HANDOFF_DITADO_F8.md` presente na raiz;
- commit documental exclusivo;
- `main` inalterada;
- SHA do commit informado e validado.
