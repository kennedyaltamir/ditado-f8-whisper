# HANDOFF_DITADO_F8.md

> Projeto: Ditado F8 Whisper  
> Repositório: `kennedyaltamir/ditado-f8-whisper`  
> Data do marco: 2026-09-15  
> Branch remota de trabalho da IA: `ai/update`  
> Branch local informada pelo usuário: `update`  
> SHA-base: `c65fe91b60f2142afa3338f20874535610562e11`  
> Base: `main` / `origin/main`

---

## 1. Objetivo e fonte de verdade

Este documento registra o estado técnico auditado do Ditado F8 Whisper antes das alterações funcionais da fase de estabilização.

Prioridade de fontes:

1. estado real do working tree local apresentado pelo usuário;
2. HEAD e histórico Git local apresentados pelo usuário;
3. refs remotas verificadas;
4. código existente;
5. documentação atualizada;
6. roadmaps/documentos históricos;
7. hipóteses técnicas, sempre identificadas como hipóteses.

O fluxo funcional principal a preservar é:

`segurar F8 -> falar -> soltar F8 -> transcrever -> copiar/colar`

O sistema deve continuar local/offline, sem telemetria e sem registrar texto integral em futuros logs por padrão.

---

## 2. Estado Git verificado

### Local do usuário — TESTADO PELO USUÁRIO

O usuário executou e forneceu a saída de:

```powershell
git status
git branch --show-current
git rev-parse HEAD
git fetch origin
git rev-parse origin/main
git log --oneline -n 10
git branch -a
```

Resultado verificado:

- branch local: `update`;
- working tree: limpo;
- HEAD local: `c65fe91b60f2142afa3338f20874535610562e11`;
- `origin/main`: `c65fe91b60f2142afa3338f20874535610562e11`;
- `main`, `update`, `origin/main` e `origin/HEAD` estavam alinhados no mesmo commit.

### Remoto da IA — VERIFICADO

- `ai/update` foi criada com sucesso a partir de `c65fe91b60f2142afa3338f20874535610562e11`;
- a branch local `update` do usuário e a branch remota `ai/update` são deliberadamente separadas;
- nenhuma alteração foi feita em `main` neste marco;
- tentativas anteriores de criar/atualizar uma branch pela integração retornaram `403 Resource not accessible by integration`; após ajuste de autorização, a criação de `ai/update` passou a funcionar.

---

## 3. Arquitetura atual

O núcleo permanece concentrado em `ditado_f8_widget.py`, que reúne responsabilidades de:

- UI Tkinter;
- configuração;
- hotkeys globais via `keyboard`;
- captura de áudio via `sounddevice`;
- seleção de dispositivo;
- estado operacional;
- persistência WAV/TXT;
- execução do `whisper-cli.exe`;
- parsing da saída do Whisper;
- histórico em memória;
- clipboard;
- simulação de `Ctrl+V`;
- shutdown.

Arquivos relevantes já identificados:

- `ditado_f8_widget.py` — núcleo atual;
- `config.json` — configuração ativa;
- `Iniciar Ditado F8 Widget.vbs` — launcher silencioso atual;
- `Iniciar Ditado F8.bat` — launcher alternativo que ainda referencia `ditado_f8.py`;
- `ditado_f8.py` — implementação legada ainda referenciada;
- `ditado_f8_widget_backup_controle.py` — backup versionado, não remover sem análise separada;
- documentação em `docs/` e roadmaps na raiz.

Não foi identificado no tree auditado `requirements.txt`, `pyproject.toml` ou suíte de testes automatizados.

---

## 4. Arquitetura alvo

A evolução deve ser incremental, sem reescrita total.

Componentes-alvo:

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

Estados-alvo:

- `IDLE`;
- `RECORDING`;
- `PROCESSING`;
- `CANCELLING`;
- `ERROR`;
- `SHUTTING_DOWN`;
- `CLOSED`.

Eventos mínimos:

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

---

## 5. Achados F01-F26

### F01 — CRITICAL — fronteira `keyboard -> Tkinter`

**CONFIRMADO.** O callback registrado por `keyboard.hook` aciona métodos que manipulam Tk diretamente. Nem todo acesso à UI passa por `root.after`.

### F02 — HIGH — sem limite máximo de gravação

**CONFIRMADO.** Frames são acumulados até stop/cancel; não existe `max_record_seconds`.

### F03 — HIGH — caminhos dependentes do ambiente

**CONFIRMADO.** Configuração/defaults contêm caminhos específicos como `C:\whispercpp\...`.

### F04 — HIGH — launcher VBS não portátil

**CONFIRMADO.** O launcher contém caminhos absolutos para Python/script; o BAT também depende de `C:\whispercpp`.

### F05 — HIGH — foco da janela de destino

**CONFIRMADO COMO RISCO REAL.** O fluxo envia `Ctrl+V` sem captura, validação e restauração segura da janela-alvo.

### F06 — HIGH — resultado Whisper sem semântica estruturada

**CONFIRMADO.** `transcribe_wav()` retorna apenas `str`; não existe `TranscriptionResult`.

### F07 — MEDIUM — parser Whisper acoplado e frágil

**CONFIRMADO.** O parsing está embutido no fluxo de transcrição e não possui testes isolados.

### F08 — MEDIUM — possível colisão de nomes

**CONFIRMADO.** O nome base usa timestamp com resolução de segundos.

### F09 — MEDIUM — microfone resolvido somente na inicialização

**CONFIRMADO.** Não há recuperação ativa/re-enumeração antes de nova sessão após falha.

### F10 — MEDIUM — `status` do callback de áudio ignorado

**CONFIRMADO.** O callback recebe `status`, mas o fluxo não o trata.

### F11 — MEDIUM — estado distribuído em booleanos

**CONFIRMADO.** O sistema não possui máquina de estados explícita.

### F12 — MEDIUM — shutdown não coordenado

**CONFIRMADO.** O fechamento não coordena adequadamente stream, thread/subprocesso e callbacks tardios de UI.

### F13 — MEDIUM — Whisper sem timeout

**CONFIRMADO.** A chamada a `subprocess.run` não define `timeout=`.

### F14 — MEDIUM — configuração sem schema/versionamento

**CONFIRMADO.** Não existe `config_version` nem validação formal.

### F15 — MEDIUM — dependências não formalizadas

**CONFIRMADO.** Não há arquivo reproduzível de dependências no tree auditado.

### F16 — MEDIUM — sem testes automatizados

**CONFIRMADO.** Não existe suíte de testes no tree auditado.

### F17 — MEDIUM — sem logging estruturado

**CONFIRMADO.** Não há infraestrutura formal de logging técnico.

### F18 — MEDIUM — privacidade/retenção não formalizadas

**CONFIRMADO.** O fluxo persiste áudio/texto e ainda não há política formal de retenção.

### F19 — MEDIUM — histórico baseado em dicionários

**CONFIRMADO.** Não existe modelo `DictationRecord`.

### F20 — LOW — backup funcional versionado

**CONFIRMADO.** `ditado_f8_widget_backup_controle.py` permanece versionado; remoção exige análise separada.

### F21 — LOW — implementação legada paralela

**CONFIRMADO / RECLASSIFICADO.** `ditado_f8.py` é legado para o widget, mas ainda é referenciado pelo BAT; não remover agora.

### F22 — LOW — `keyboard.unhook_all()`

**CONFIRMADO.** O shutdown remove hooks globalmente em vez de apenas o hook próprio.

### F23 — LOW — conversão de áudio sem clamp

**CONFIRMADO.** A conversão para `int16` não aplica `np.clip` previamente.

### F24 — ARCHITECTURAL — concentração de responsabilidades

**CONFIRMADO.** `process_audio()` e o widget concentram persistência, transcrição, parsing, histórico, clipboard, colagem, status e tratamento de erro.

### F25 — HIGH — configuração de persistência diverge do comportamento

**CONFIRMADO COMO INCONSISTÊNCIA A CORRIGIR.** Existem `save_audio` e `save_txt`, mas o fluxo auditado salva WAV/TXT diretamente e precisa ser corrigido para respeitar essas flags de fato.

Critério futuro:

- `save_audio=false` => nenhum WAV criado;
- `save_txt=false` => nenhum TXT criado;
- a transcrição e saída devem continuar funcionando conforme aplicável.

### F26 — MEDIUM — idempotência dos eventos

**PENDENTE DE IMPLEMENTAÇÃO E TESTE.** Verificar explicitamente:

- `HOTKEY_DOWN` duplicado;
- `HOTKEY_UP` sem gravação;
- `CANCEL` duplicado;
- `STOP` após `CANCEL`;
- `CLOSE` durante `RECORDING`;
- `CLOSE` durante `PROCESSING`;
- `TRANSCRIPTION_SUCCESS` após `SHUTDOWN`.

Eventos inválidos para o estado corrente devem ser ignorados ou tratados deterministicamente, sem corromper estado.

---

## 6. Divergências de documentação já identificadas

- `docs/PROJETO.md` trata a externalização de configuração como futura, mas `config.json` já existe;
- `PROXIMAS_FASES_DITADO_F8.md` registra thread safety visual como resolvida, porém callbacks globais ainda podem chegar a operações Tk fora da thread principal;
- `docs/PROTOCOLO_IA.md` afirma que a IA não possui acesso ao GitHub; isso não corresponde ao ambiente atual, que possui leitura e agora também conseguiu criar/escrever em branch autorizada.

Roadmaps históricos permanecem contexto, não autoridade superior ao código real.

---

## 7. Ordem de implementação

### Fase A — Estabilização

1. corrigir a fronteira `keyboard -> Tkinter`;
2. criar event dispatch mínimo;
3. introduzir máquina de estados;
4. corrigir shutdown coordenado;
5. implementar timeout do Whisper;
6. criar resultado estruturado de transcrição;
7. distinguir sucesso, ausência de fala, erro do engine, executável ausente, modelo ausente, timeout e saída inválida;
8. implementar `max_record_seconds`;
9. tratar status do callback de áudio;
10. melhorar recuperação do dispositivo;
11. corrigir foco/restauração segura da janela-alvo;
12. fazer `save_audio`/`save_txt` controlarem a persistência.

### Fase B — Fundação

13. `ConfigService`/validação;
14. `config_version`;
15. `WhisperOutputParser`;
16. identificador único de arquivos;
17. `DictationRecord`;
18. `StorageService`;
19. `OutputController`;
20. logging estruturado;
21. dependências formalizadas;
22. testes automatizados.

### Fase C — Produto

23. histórico persistente;
24. metadados;
25. modo compacto;
26. system tray.

### Fase D — Distribuição

27. diagnóstico de ambiente;
28. PyInstaller;
29. instalador;
30. estratégia de atualização.

---

## 8. Requisitos especiais

### Foco de janela

Não enviar `Ctrl+V` a uma janela potencialmente errada. A implementação futura deve:

- identificar a janela ativa relevante;
- armazenar um identificador seguro;
- validar que a janela ainda existe;
- tratar janela minimizada/perda de foco;
- considerar diferenças de privilégio;
- validar em aplicações reais antes de declarar concluído.

### Shutdown

O fluxo futuro deve distinguir ao menos `RUNNING`, `SHUTTING_DOWN` e `CLOSED`, impedir novas gravações durante shutdown, encerrar stream, tratar subprocesso Whisper e impedir callbacks tardios de modificar UI destruída.

### Privacidade

- manter processamento local/offline;
- não adicionar telemetria;
- não gravar texto integral em logs por padrão;
- respeitar `save_audio` e `save_txt` realmente.

### Legado

Não remover imediatamente `ditado_f8.py` nem `ditado_f8_widget_backup_controle.py`. Primeiro buscar referências, verificar launchers, documentar a decisão e, se aplicável, remover em commit separado após validação.

---

## 9. Testes e evidências

### STATIC

**PASS / auditoria remota:** inspeção do código principal, configuração, launchers, documentação e histórico do commit base.

### GIT LOCAL

**PASS / executado pelo usuário:** branch, HEAD, `origin/main`, log, branches e working tree foram verificados; estado estava limpo e alinhado no SHA-base.

### GITHUB WRITE

**PASS:** `ai/update` foi criada a partir do SHA-base após ajuste de autorização da integração.

### AUTOMATED

**NOT_EXECUTED:** ainda não existe suíte automatizada no tree auditado.

### MANUAL

**NOT_EXECUTED NESTE MARCO:**

- F8 hold;
- F8 toggle;
- botão;
- cancelamento;
- microfone;
- Whisper real;
- clipboard/auto-paste;
- foco;
- shutdown durante gravação/processamento;
- timeout;
- limite de gravação;
- executável/modelo ausentes.

Não considerar essas funções validadas apenas pela inspeção estática.

---

## 10. Protocolo de continuidade

Antes de cada implementação, registrar:

- problema;
- arquivos alterados;
- arquivos criados;
- risco;
- forma de validação;
- critério objetivo de aceite.

Depois da implementação:

- revisar alterações;
- executar validação estática aplicável;
- executar testes automatizados quando existirem;
- solicitar testes manuais que dependam do Windows/áudio/Whisper;
- diferenciar `IMPLEMENTADO`, `VERIFICADO ESTATICAMENTE`, `TESTADO PELO USUÁRIO`, `NÃO TESTADO` e `BLOQUEADO`.

Após cada marco, atualizar este handoff com:

- estado atual;
- arquivos modificados/criados/removidos;
- testes executados e não executados;
- riscos restantes;
- SHA do marco;
- próximo passo.

Regras Git:

- `main` permanece referência e não deve receber desenvolvimento direto;
- a branch local do usuário permanece `update` até instrução explícita;
- a branch remota da IA é `ai/update`;
- não usar `git add .` sem revisão;
- não usar operações destrutivas (`reset --hard`, `clean`, `restore .`, `checkout -- .`, `push --force`) sem autorização explícita;
- preservar trabalho local existente.

---

## 11. Estado do marco M1

### IMPLEMENTADO

- branch remota `ai/update` criada a partir do SHA-base correto;
- este handoff preparado como primeiro artefato da branch.

### VERIFICADO ESTATICAMENTE

- arquitetura atual e alvo;
- F01-F26;
- divergências documentais;
- prioridades de estabilização.

### TESTADO PELO USUÁRIO

- inspeção Git local completa informada nesta sessão.

### NÃO TESTADO

- execução do aplicativo e todos os testes funcionais dependentes do Windows/áudio/Whisper.

### Próximo passo

Iniciar a Fase A pelo item 1: corrigir a fronteira `keyboard -> Tkinter`, preservando o comportamento funcional existente e preparando o event dispatch mínimo.
