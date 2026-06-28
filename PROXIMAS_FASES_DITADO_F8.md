# PROXIMAS FASES — DITADO F8 WHISPER

## 1. Resumo Executivo

O **Ditado F8 Whisper** é um aplicativo local para Windows 11 focado em produtividade e privacidade. Ele permite a transcrição de voz para texto utilizando o motor Whisper local (`whisper-cli.exe`), sem dependência de internet ou APIs em nuvem. O sistema opera através de um widget construído em Tkinter, escuta hotkeys globais para gravação de áudio, processa a transcrição em background e realiza a colagem automática do texto no campo ativo do usuário.

Este documento serve como o guia oficial de arquitetura, estado atual e planejamento futuro, garantindo que o desenvolvimento possa ser pausado e retomado a qualquer momento sem perda de contexto.

---

## 2. Estado Atual Homologado/Implementado

As seguintes fases já foram implementadas, testadas localmente e commitadas no repositório:

* **Fase 1A — Arquitetura de configuração:** Implementado o `config.json`, suporte a hotkey flexível, modos `hold` e `toggle`, tecla de cancelamento, `auto_paste` e `always_on_top`.
* **Fase 1B — Interface de configurações:** Implementado o botão ⚙ no widget e a janela `Toplevel` para edição visual das preferências, com salvamento direto no JSON.
* **Fase 1C — Configurações em tempo real:** Implementada a aplicação de configurações sem necessidade de reiniciar o app (recarregamento de hooks globais e variáveis de estado).
* **Fase 2A — Botão visual Gravar/Parar:** Implementado o botão principal na interface que funciona por clique, reaproveitando o fluxo seguro de gravação.
* **Fase 2B — Contador de gravação:** Implementado o timer (`MM:SS`) atualizado via `root.after`.
* **Fase 2C — Indicador de volume:** Implementada a barra visual de captação baseada no cálculo RMS do áudio.
* **Fase 2D — Polimento visual inicial:** Implementada a reorganização do layout para acomodar os novos controles, mantendo a estética premium.
* **Fase 3A — Histórico recente no widget:** Implementado o histórico em memória dos últimos 10 ditados da sessão, exibindo os 3 mais recentes na interface com ações de Copiar, abrir TXT, Usar e Limpar.

### Últimos Commits Relevantes
* `d304d6e` feat: criar ditado f8 whisper local
* `f9ba1cb` docs: adicionar roadmap de features do ditado f8
* `46ea823` docs: adicionar protocolo de ia e arquitetura do ditado f8
* `d442c12` chore: ignorar arquivos locais do patch engine
* `98366fd` chore: reforcar ignore de copias locais
* `50f3fa4` chore: ignorar ferramentas locais temporarias
* `0a6b9f7` feat: adicionar configuracao de hotkey e modo de gravacao
* `b40c9ff` feat: adicionar botao gravar contador e volume
* `a5dbc3e` chore: ignorar backups e contexto local
* `dee8233` feat: adicionar historico recente de ditados no widget

---

## 3. Arquitetura Atual

A arquitetura do projeto é centralizada e orientada a eventos:
* **`ditado_f8_widget.py`:** Concentra toda a lógica principal (UI, captura de áudio, orquestração do Whisper e manipulação de clipboard).
* **`config.json`:** Arquivo local que atua como fonte da verdade para as configurações do usuário.
* **Motor de Transcrição:** O `whisper-cli.exe` é chamado via subprocesso em uma thread secundária para não congelar a interface gráfica.
* **Armazenamento:** Os arquivos `.wav` e `.txt` são salvos localmente na pasta `gravacoes_ditado`.
* **Thread Safety:** A UI roda no loop principal do Tkinter. Nenhuma alteração visual (como contador, volume ou histórico) é feita diretamente a partir de callbacks de áudio ou threads secundárias; tudo é despachado de forma segura utilizando `root.after`.

---

## 4. Regras Supremas do Projeto

Para garantir a estabilidade do sistema, qualquer IA ou desenvolvedor que atuar neste projeto deve seguir estas regras inegociáveis:

1. **Não quebrar o fluxo principal:** A gravação, transcrição e colagem devem permanecer rápidas e confiáveis.
2. **Não apagar arquivos do usuário:** Nunca delete arquivos `.wav` ou `.txt` existentes.
3. **Não mexer em `whisper-bin-x64/`:** Os binários e modelos são dependências externas intocáveis.
4. **Não commitar arquivos pesados ou sensíveis:** Modelos `.bin`, gravações, transcrições e backups locais (`.backups_atualizar/`) são estritamente proibidos no Git.
5. **Não reescrever o app inteiro sem necessidade:** Evoluções devem ser incrementais.
6. **Não introduzir dependências novas sem justificativa:** Manter o projeto leve.
7. **Sempre entregar patches completos:** Utilizar o formato exigido pelo Patch Engine (`atualizar.py`).
8. **Sempre testar antes de commitar:** A validação local pelo usuário é obrigatória.
9. **Sempre preservar o `config.json`:** Garantir que exista um fallback seguro (`DEFAULT_CONFIG`) caso o arquivo seja corrompido ou apagado.

---

## 5. Fluxo Atual do Aplicativo

O aplicativo suporta múltiplos fluxos de interação que coexistem pacificamente:

* **Hotkey Hold:** `Segurar hotkey > falar > soltar > transcrever > salvar > copiar/colar`
* **Hotkey Toggle:** `Apertar hotkey > falar > apertar novamente > transcrever > salvar > copiar/colar`
* **Botão Visual:** `Clicar Gravar > falar > clicar Parar > transcrever > salvar > copiar/colar`
* **Cancelamento:** `Gravando > Cancelar/Esc/F12 > descartar áudio > não transcrever > não salvar`
* **Histórico:** `Transcrição bem-sucedida > adiciona ao histórico em memória > exibe últimos 3 no widget`

---

## 6. Próximas Fases Recomendadas

As fases abaixo detalham o roteiro futuro do projeto. Elas devem ser implementadas uma a uma.

### FASE 3B — ORGANIZAÇÃO DE GRAVAÇÕES POR DATA
* **Objetivo:** Organizar os arquivos `.wav` e `.txt` em subpastas por data (ex: `gravacoes_ditado/2026-06-28/20260628_030933.wav`).
* **Implementação recomendada:** Adicionar a chave `"organize_by_date": false` no `config.json`. Manter desligado por padrão inicialmente. Se ativado, criar a subpasta `YYYY-MM-DD` e salvar os arquivos nela.
* **Critérios de aceite:** Se `false`, o comportamento atual permanece. Se `true`, cria a subpasta. Não quebra o histórico em memória, nem os botões de abrir TXT ou ouvir áudio. Não move arquivos antigos nem apaga nada.
* **Riscos:** Quebrar caminhos absolutos no histórico ou confundir a abertura da pasta raiz.

### FASE 3C — METADADOS JSON POR DITADO
* **Objetivo:** Criar um arquivo `.json` para cada ditado contendo metadados ricos (ex: `20260628_030933.json`).
* **Conteúdo sugerido:** timestamp, texto, wav_path, txt_path, duration_seconds, hotkey usada, recording_mode, auto_paste, model_path, language, microphone_name, status e erros.
* **Implementação recomendada:** Adicionar a chave `"save_metadata": true`. Salvar o JSON após a transcrição usando o mesmo timestamp base.
* **Critérios de aceite:** JSON criado apenas para transcrições bem-sucedidas. Não quebra a geração de TXT/WAV.

### FASE 3D — HISTÓRICO PERSISTENTE SIMPLES
* **Objetivo:** Ao abrir o app, carregar o histórico recente a partir dos arquivos `.json` ou `.txt` locais.
* **Implementação recomendada:** NÃO usar SQLite ainda. Ler os últimos N ditados da pasta (respeitando a organização por data, se ativa) e popular o `self.history_items` na inicialização.
* **Critérios de aceite:** Fechar e abrir o app mantém o histórico recente visível. Não reprocessa áudio, não chama o Whisper e não trava a inicialização.

### FASE 4A — MODO COMPACTO / EXPANDIDO
* **Objetivo:** Criar uma versão minimalista do widget para ocupar menos espaço na tela.
* **Implementação recomendada:** Adicionar a chave `"compact_mode": false`. Criar botões `Compactar` e `Expandir` na UI. O modo compacto deve exibir apenas o status, a hotkey e os botões essenciais (Gravar/Parar, Configurações).
* **Critérios de aceite:** Alterna sem reiniciar o app, não perde o histórico em memória, não quebra a gravação e salva a preferência no JSON.

### FASE 4B — MELHORIAS VISUAIS DA TELA DE CONFIGURAÇÕES
* **Objetivo:** Expandir a tela de configurações para incluir as novas opções (organizar por data, salvar metadados, modo compacto).
* **Cuidado:** A seleção de microfone e modelo pela UI é delicada e deve ser tratada com cautela para não quebrar o motor de áudio.

### FASE 5A — SYSTEM TRAY
* **Objetivo:** Permitir minimizar o aplicativo para a bandeja do sistema (perto do relógio).
* **Critérios de aceite:** Fechar a janela pode apenas ocultá-la se o modo tray estiver ativo. Deve possuir opções de "Mostrar/Ocultar" e "Sair".
* **Risco:** Introdução de novas dependências (ex: `pystray`, `Pillow`) que podem complicar o empacotamento.

### FASE 5B — INICIAR COM WINDOWS
* **Objetivo:** Criar opção para iniciar o aplicativo automaticamente com o Windows.
* **Implementação recomendada:** Começar com uma configuração manual documentada (ex: atalho na pasta Startup) e, futuramente, automatizar via código.

### FASE 5C — PREVENIR MÚLTIPLAS INSTÂNCIAS
* **Objetivo:** Evitar que o usuário abra dois widgets ao mesmo tempo.
* **Implementação recomendada:** Usar lock file, porta local ou mutex do Windows. Se já estiver aberto, focar a janela existente.

### FASE 5D — LOGS TÉCNICOS
* **Objetivo:** Criar um arquivo de log local (`logs/ditado_f8.log`) para debugging.
* **Critérios de aceite:** Registrar abertura, microfone, início/fim de gravação, caminhos e erros. Não logar textos completos se um modo de privacidade estiver ativo.

### FASE 6A — EMPACOTAMENTO EM EXE
* **Objetivo:** Gerar um executável `.exe` standalone utilizando PyInstaller.
* **Cuidado:** Lidar corretamente com caminhos relativos e manter a pasta `whisper-bin-x64` externa ou empacotada separadamente para não gerar um executável gigantesco.

### FASE 6B — INSTALADOR
* **Objetivo:** Criar um instalador Windows (ex: Inno Setup ou NSIS). Deve ser feito apenas quando o app estiver totalmente estabilizado.

### FASE 7 — PERFIS DE USO
* **Objetivo:** Criar perfis rápidos (ex: Rápido = modelo small, Qualidade = modelo medium).
* **Cuidado:** Não apagar modelos locais nem baixar arquivos pesados automaticamente sem autorização explícita.

### FASE 8 — MODO PRIVACIDADE
* **Objetivo:** Permitir que o usuário opte por não salvar áudio, TXT, histórico ou metadados no disco.
* **Cuidado:** A UI e os botões de ação (Abrir TXT, Ouvir Áudio) devem ser ajustados para lidar graciosamente com a ausência desses arquivos.

---

## 7. Ordem Recomendada de Execução

A ordem abaixo foi desenhada para minimizar riscos, construindo a fundação de dados antes de avançar para integrações complexas com o sistema operacional:

1. **Fase 3B** — Organização por data (desligada por padrão).
2. **Fase 3C** — Metadados JSON por ditado.
3. **Fase 3D** — Histórico persistente simples.
4. **Fase 4A** — Modo compacto/expandido.
5. **Fase 4B** — Configurações avançadas na UI.
6. **Fase 5D** — Logs técnicos.
7. **Fase 5C** — Prevenir múltiplas instâncias.
8. **Fase 5A** — System Tray.
9. **Fase 5B** — Iniciar com Windows.
10. **Fase 6A** — EXE (PyInstaller).
11. **Fase 6B** — Instalador.
12. **Fase 7** — Perfis de uso.
13. **Fase 8** — Privacidade.

---

## 8. Critérios Globais de Aceite

Antes de qualquer commit, o desenvolvedor/IA deve garantir que:
- [ ] O app abre silenciosamente pelo `.vbs` (sem console).
- [ ] A gravação funciona perfeitamente pelo botão visual.
- [ ] A gravação funciona perfeitamente pela hotkey (modos hold e toggle).
- [ ] O cancelamento aborta a gravação sem gerar arquivos lixo.
- [ ] A transcrição ocorre e salva os arquivos `.wav` e `.txt` corretamente.
- [ ] O histórico em memória é atualizado e renderizado sem travar a UI.
- [ ] As configurações são aplicadas em tempo real sem reiniciar.
- [ ] Nenhum arquivo do usuário foi apagado.
- [ ] O Git está limpo e arquivos ignorados não estão no stage.

---

## 9. Comandos Git Padrão

Para manter o repositório seguro, **nunca use `git add .` sem revisar**.

Fluxo recomendado:
```powershell
git status
git add ditado_f8_widget.py docs/
git commit -m "feat: descricao clara da funcionalidade"
git push
git status
```

Para commitar este documento de planejamento:
```powershell
git add PROXIMAS_FASES_DITADO_F8.md
git commit -m "docs: registrar proximas fases do ditado f8"
git push
```

---

## 10. Arquivos que Não Devem Ser Commitados

O `.gitignore` já está configurado, mas é vital lembrar de **nunca** forçar a adição de:
* `whisper-bin-x64/` e modelos `.bin`
* `gravacoes_ditado/` e arquivos `.wav`, `.mp3`, `.m4a`, `.flac`, `.ogg`
* `.backups_atualizar/` e `Cópia do projeto/`
* `ZProjetoCompleto*.txt` e `resposta.txt`
* `atualizar.py` e `gerarcontexto.py` (salvo se houver atualização na ferramenta)
* Pastas de cache como `__pycache__/`

---

## 11. Como Retomar o Projeto no Futuro

Siga este passo a passo para voltar ao desenvolvimento sem perder o ritmo:

1. Abra o PowerShell ou Terminal.
2. Navegue até a pasta do projeto: `cd "C:\whispercpp"`
3. Confira se a árvore de trabalho está limpa: `git status`
4. Leia este documento e escolha a próxima fase a ser implementada.
5. Gere o contexto atualizado do projeto: `python gerarcontexto.py`
6. Envie o contexto (`ZProjetoCompleto.txt`) para a IA Implementadora solicitando a fase escolhida.
7. (Opcional) Revise a proposta com uma IA Coordenadora/Revisora.
8. Salve a resposta da IA em `resposta.txt`.
9. Aplique o código com segurança: `python atualizar.py`
10. Teste exaustivamente o aplicativo localmente.
11. Faça o commit e o push das alterações.

---

## 12. Próxima Fase Imediata Recomendada

**Próxima fase recomendada: Fase 3B — Organização de gravações por data (desligada por padrão no config).**

*Motivo:* Esta fase melhora a organização dos arquivos a longo prazo e prepara o terreno estrutural para a geração de metadados (Fase 3C) e para a persistência do histórico (Fase 3D). Mantê-la desligada por padrão garante que o risco de quebra do fluxo atual seja praticamente zero durante a homologação.
