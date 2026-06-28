# Roadmap de Features — Ditado F8 Whisper

## 1. Visão geral do projeto

O **Ditado F8 Whisper** é um mini aplicativo local para Windows 11 criado para transformar voz em texto usando Whisper local. O objetivo principal é permitir que o usuário dite textos em qualquer campo ativo do computador, de forma rápida, prática e privada.

Fluxo atual principal:

```txt
Segurar F8 > falar > soltar F8 > transcrever > colar no campo ativo
```

O projeto já está funcional e utilizável no dia a dia. A versão atual permite gravar áudio, transcrever, salvar o áudio, salvar a transcrição em `.txt`, mostrar o último texto no widget e colar automaticamente no campo ativo.

Este documento lista as melhorias que podem ser implementadas para transformar o projeto em uma ferramenta mais profissional, configurável, estável e confortável para uso diário.

---

# 2. Estado atual aprovado

## 2.1 Funcionalidades já existentes

A versão atual já possui:

* Widget visual premium.
* Janela sem borda.
* Botão de minimizar.
* Botão de fechar.
* Possibilidade de arrastar o widget com o mouse.
* Status visual:

  * Pronto.
  * Gravando.
  * Carregando sua voz.
  * Texto colado.
  * Erro.
* Atalho global com tecla F8.
* Modo de gravação segurando F8.
* Transcrição local usando `whisper-cli.exe`.
* Modelo atual: `ggml-medium.bin`.
* Microfone selecionado automaticamente pelo nome `Iriun`.
* Salvamento automático do áudio `.wav`.
* Salvamento automático da transcrição `.txt`.
* Botão para abrir a pasta dos testes.
* Botão para ouvir o último áudio.
* Botão para abrir o último TXT.
* Botão para copiar o último texto.
* Ícone personalizado.
* Inicialização sem tela preta usando `.vbs`.
* Projeto salvo no GitHub.
* `.gitignore` protegendo:

  * Modelos grandes.
  * Binários do Whisper.
  * Gravações locais.
  * Pasta `.history`.
  * Arquivos temporários.

---

# 3. Objetivo das próximas melhorias

O objetivo das próximas versões é deixar o Ditado F8 Whisper mais próximo de um aplicativo profissional de produtividade.

As melhorias devem focar em:

1. Melhor usabilidade.
2. Mais opções de controle.
3. Mais personalização.
4. Melhor design.
5. Mais segurança contra perda de texto.
6. Melhor histórico.
7. Configurações editáveis.
8. Menos dependência de mexer diretamente no código.
9. Preparação para empacotamento como app real no Windows.

---

# 4. Melhorias de atalho e modo de gravação

## 4.1 Permitir trocar a tecla de ativação

Atualmente o sistema usa somente:

```txt
F8
```

Melhoria desejada:

Permitir que o usuário escolha outra tecla, por exemplo:

```txt
F6
F7
F8
F9
F10
Ctrl + Espaço
Ctrl + Alt + D
Alt + Q
Mouse Button 4
Mouse Button 5
```

Motivo:

Nem sempre F8 será confortável. Em alguns programas, F8 pode ter função própria. Em outros casos, o usuário pode preferir uma tecla mais próxima da mão ou uma combinação que evite acionamento acidental.

Implementação ideal:

Criar uma configuração em arquivo:

```txt
config.json
```

Exemplo:

```json
{
  "hotkey": "f8"
}
```

No futuro, o próprio widget poderá ter uma tela de configurações para alterar isso sem editar arquivo manualmente.

---

## 4.2 Modo 1 — Segurar para falar

Este é o modo atual.

Fluxo:

```txt
Segura F8 > grava
Solta F8 > para gravação, transcreve e cola
```

Vantagens:

* Rápido.
* Seguro.
* Evita esquecer o microfone ligado.
* Ideal para frases curtas e médias.
* Ideal para responder mensagens, escrever prompts, anotar ideias e ditar pequenos blocos de texto.

Esse modo deve continuar sendo o padrão.

---

## 4.3 Modo 2 — Apertar uma vez para começar e apertar de novo para parar

Novo modo desejado.

Fluxo:

```txt
Aperta F8 uma vez > começa a gravar
Aperta F8 de novo > para, transcreve e cola
```

Vantagens:

* Melhor para ditados longos.
* O usuário não precisa ficar segurando a tecla.
* Mais confortável para textos grandes.
* Útil para escrever documentos, prompts longos, ideias extensas e explicações.

Cuidados necessários:

* O widget precisa mostrar claramente que ainda está gravando.
* Deve ter contador de tempo.
* Deve ter alerta visual forte para o usuário não esquecer ligado.
* Pode ter limite máximo de gravação, por exemplo 2, 5 ou 10 minutos.
* Pode ter botão de cancelar gravação.

Configuração sugerida:

```json
{
  "recording_mode": "hold"
}
```

Valores possíveis:

```txt
hold
toggle
```

Onde:

* `hold` = segurar para falar.
* `toggle` = apertar para iniciar e apertar novamente para parar.

---

## 4.4 Modo 3 — Botão visual no widget

Além da tecla, o widget poderia ter um botão grande:

```txt
🎤 Gravar
```

Fluxo:

```txt
Clica no botão > começa a gravar
Clica novamente > para e transcreve
```

Vantagens:

* Útil quando o usuário não quer usar teclado.
* Facilita uso em telas touch.
* Facilita para usuários menos técnicos.
* Ajuda quando o atalho global falha em algum programa.

---

## 4.5 Atalho para cancelar gravação

Adicionar uma tecla de emergência, por exemplo:

```txt
Esc
```

Função:

```txt
Cancelar gravação atual sem transcrever e sem colar
```

Motivo:

Às vezes o usuário começa a falar errado, é interrompido ou percebe que está no campo errado.

Fluxo:

```txt
Gravando > apertar Esc > descarta o áudio atual > volta para Pronto
```

Configuração sugerida:

```json
{
  "cancel_hotkey": "esc"
}
```

---

## 4.6 Atalho para copiar último texto

Adicionar um atalho para copiar novamente o último texto transcrito.

Exemplo:

```txt
Ctrl + Alt + C
```

Motivo:

Se o texto não colar no lugar certo, o usuário consegue recuperar rapidamente.

---

## 4.7 Atalho para repetir última colagem

Adicionar função:

```txt
Colar novamente o último texto
```

Exemplo de atalho:

```txt
Ctrl + Alt + V
```

Motivo:

Às vezes o texto foi transcrito corretamente, mas o campo ativo não recebeu a colagem.

---

# 5. Melhorias no design e experiência visual

## 5.1 Melhorar o visual geral do widget

A versão atual já está muito melhor que a primeira, mas ainda pode evoluir para uma aparência mais próxima de aplicativo comercial.

Melhorias possíveis:

* Layout mais refinado.
* Espaçamentos mais equilibrados.
* Botões com aparência mais moderna.
* Ícones melhores.
* Tipografia mais profissional.
* Animações leves.
* Melhor hierarquia visual.
* Status mais claros.
* Tema escuro premium.
* Tema claro opcional.
* Tema compacto.

---

## 5.2 Criar modo compacto

Modo compacto seria uma versão pequena do widget.

Exemplo:

```txt
🎤 Pronto — F8 ativo
```

Tamanho aproximado:

```txt
280 x 70
```

Vantagens:

* Ocupa menos espaço.
* Pode ficar sempre no canto da tela.
* Ideal para uso diário.

O modo completo continuaria mostrando:

* Último texto.
* Último áudio.
* Botões.
* Configurações.

O modo compacto mostraria apenas:

* Ícone.
* Status.
* Tecla ativa.
* Pequeno indicador de gravação.

---

## 5.3 Criar modo expandido

Modo expandido seria a tela atual ou uma versão ainda maior com mais detalhes.

Poderia mostrar:

* Últimos textos.
* Histórico recente.
* Botões de ação.
* Configurações rápidas.
* Tempo de gravação.
* Microfone selecionado.
* Modelo selecionado.
* Pasta de saída.

---

## 5.4 Botão para alternar compacto/expandido

Adicionar botão:

```txt
⛶
```

Ou:

```txt
Compactar
Expandir
```

Fluxo:

```txt
Modo grande > clicar > modo compacto
Modo compacto > clicar > modo grande
```

---

## 5.5 Indicador visual de volume do microfone

Adicionar uma barrinha simples mostrando se o microfone está captando som.

Exemplo:

```txt
▁ ▂ ▃ ▅ ▇
```

Vantagens:

* O usuário sabe se o microfone está funcionando.
* Ajuda a perceber se está mudo.
* Ajuda a ajustar distância do microfone.
* Ajuda a detectar ruído ambiente.

---

## 5.6 Contador de tempo de gravação

Enquanto estiver gravando, mostrar:

```txt
Gravando... 00:07
```

Vantagens:

* Útil no modo toggle.
* Evita gravações longas sem querer.
* Dá sensação de controle.

---

## 5.7 Efeito visual durante gravação

Quando estiver gravando:

* Borda vermelha pulsando.
* Ponto vermelho piscando.
* Texto “Gravando...” maior.
* Fundo levemente avermelhado.
* Ícone de microfone ativo.

Objetivo:

Evitar que o usuário esqueça que está gravando.

---

## 5.8 Efeito visual durante transcrição

Quando estiver processando:

* Cor amarela.
* Texto “Carregando sua voz...”.
* Pequena animação de pontos:

  * `Carregando sua voz.`
  * `Carregando sua voz..`
  * `Carregando sua voz...`

---

## 5.9 Tema personalizado

Permitir escolher tema:

```txt
Escuro
Claro
Azul
Verde
Minimalista
```

Configuração sugerida:

```json
{
  "theme": "dark"
}
```

---

# 6. Melhorias de configuração

## 6.1 Criar arquivo `config.json`

Hoje várias configurações estão fixas dentro do código.

Exemplos:

```txt
HOTKEY = "f8"
MIC_NAME_CONTAINS = "Iriun"
MODEL_PATH = ...
SAVE_DIR = ...
```

Melhoria:

Criar arquivo:

```txt
config.json
```

Exemplo:

```json
{
  "hotkey": "f8",
  "cancel_hotkey": "esc",
  "recording_mode": "hold",
  "microphone_name_contains": "Iriun",
  "model_path": "C:\\whispercpp\\whisper-bin-x64\\Release\\models\\ggml-medium.bin",
  "whisper_dir": "C:\\whispercpp\\whisper-bin-x64\\Release",
  "save_dir": "C:\\whispercpp\\gravacoes_ditado",
  "language": "pt",
  "theme": "dark",
  "always_on_top": true,
  "auto_paste": true,
  "save_audio": true,
  "save_txt": true
}
```

Vantagens:

* Facilita mudar comportamento.
* Evita editar código.
* Permite criar tela de configurações depois.
* Ajuda a transformar em app real.

---

## 6.2 Tela de configurações

Adicionar botão:

```txt
⚙ Configurações
```

Opções possíveis:

* Tecla de gravação.
* Modo de gravação.
* Microfone.
* Modelo Whisper.
* Pasta de gravações.
* Idioma.
* Colar automaticamente.
* Salvar áudio.
* Salvar TXT.
* Sempre no topo.
* Tema.
* Sons ligados/desligados.
* Limite de tempo por gravação.

---

## 6.3 Seleção de microfone pelo widget

Hoje o sistema procura pelo nome:

```txt
Iriun
```

Melhoria:

Mostrar lista de microfones disponíveis:

```txt
Microfone (Iriun Webcam)
Headset (Q3)
Microfone Realtek
```

Permitir escolher um e salvar no `config.json`.

---

## 6.4 Seleção de modelo Whisper

Permitir escolher modelo:

```txt
small
medium
large
```

Ou caminho manual:

```txt
C:\whispercpp\whisper-bin-x64\Release\models\ggml-medium.bin
```

Vantagens:

* Modelo menor para velocidade.
* Modelo maior para qualidade.
* Testes comparativos.

---

## 6.5 Configurar idioma

Atualmente o idioma está fixado como português:

```txt
-l pt
```

Permitir opções:

```txt
pt
en
es
auto
```

Vantagens:

* Ditado em português.
* Ditado em inglês.
* Ditado em espanhol.
* Detecção automática quando necessário.

---

# 7. Melhorias no salvamento de arquivos

## 7.1 Melhorar organização da pasta de gravações

Hoje os arquivos ficam todos em:

```txt
gravacoes_ditado/
```

Melhoria:

Organizar por data:

```txt
gravacoes_ditado/
  2026-06-28/
    20260628_030933.wav
    20260628_030933.txt
```

Vantagens:

* Pasta mais limpa.
* Fácil localizar testes por dia.
* Mais organizado para uso contínuo.

---

## 7.2 Salvar metadados de cada ditado

Criar arquivo `.json` para cada gravação.

Exemplo:

```txt
20260628_030933.json
```

Conteúdo:

```json
{
  "timestamp": "2026-06-28 03:09:33",
  "audio_file": "20260628_030933.wav",
  "text_file": "20260628_030933.txt",
  "text": "Agora estou fazendo o teste...",
  "duration_seconds": 4.8,
  "model": "ggml-medium.bin",
  "microphone": "Iriun Webcam",
  "language": "pt",
  "recording_mode": "hold"
}
```

Vantagens:

* Permite criar histórico.
* Permite auditoria.
* Ajuda a comparar desempenho.
* Ajuda a depurar problemas.

---

## 7.3 Criar histórico em SQLite

No futuro, ao invés de depender só de arquivos, pode ser criado um banco local:

```txt
ditado_history.sqlite
```

Tabela:

```txt
dictations
```

Campos:

* id.
* data/hora.
* texto.
* caminho do áudio.
* caminho do TXT.
* duração.
* modelo.
* microfone.
* idioma.
* modo de gravação.
* status.

Vantagens:

* Busca rápida.
* Histórico dentro do app.
* Filtros por data.
* Exportação.
* Estatísticas de uso.

---

## 7.4 Botão de limpar histórico com segurança

Adicionar botão:

```txt
Limpar histórico
```

Mas com cuidado.

Opções melhores:

```txt
Mover arquivos antigos para backup
Apagar apenas gravações com mais de X dias
Manter últimos 100 registros
```

Recomendação:

Não apagar automaticamente no início. Primeiro implementar:

```txt
Arquivar histórico antigo
```

---

# 8. Melhorias de histórico e produtividade

## 8.1 Mostrar últimos ditados

O widget poderia mostrar os últimos 5 ou 10 textos transcritos.

Exemplo:

```txt
Últimos ditados:
1. Agora estou fazendo o teste...
2. Quero redigir um prompt...
3. Me ajude a organizar...
```

Vantagens:

* Recuperar texto rapidamente.
* Evitar perda se colar no lugar errado.
* Ajudar em trabalhos longos.

---

## 8.2 Buscar no histórico

Criar busca por palavra.

Exemplo:

```txt
Buscar: GitHub
```

Mostra todos os ditados que contêm “GitHub”.

---

## 8.3 Favoritar ditados

Adicionar botão:

```txt
⭐ Favoritar
```

Uso:

* Salvar prompts importantes.
* Guardar textos recorrentes.
* Marcar frases úteis.

---

## 8.4 Exportar histórico

Permitir exportar histórico em:

```txt
.txt
.md
.csv
.json
```

Vantagens:

* Criar relatórios.
* Salvar anotações.
* Reutilizar em outros projetos.

---

## 8.5 Botão “Enviar para arquivo de notas”

Criar um arquivo fixo:

```txt
ANOTACOES_DITADO.md
```

Toda vez que o usuário quiser, pode mandar o último texto para esse arquivo.

Formato:

```md
## 2026-06-28 03:15

Texto ditado aqui...
```

Uso:

* Anotações rápidas.
* Ideias.
* Logs pessoais.
* Rascunhos de prompts.

---

# 9. Melhorias na transcrição

## 9.1 Melhor tratamento de ruídos

Hoje o sistema já ignora algumas saídas como:

```txt
[Música]
[Som]
```

Podemos reforçar filtros para remover:

```txt
[Música]
[Music]
[Som de fundo]
[Ruído]
[Silêncio]
[Aplausos]
[Inaudível]
```

Cuidado:

Não remover texto real por engano.

---

## 9.2 Correção automática de pontuação

Whisper pode transcrever bem, mas nem sempre pontua perfeitamente.

Podemos criar uma etapa opcional:

```txt
Corrigir pontuação
```

Exemplo:

Entrada:

```txt
olá quero que você me ajude a criar um documento para o projeto
```

Saída:

```txt
Olá, quero que você me ajude a criar um documento para o projeto.
```

Essa correção poderia ser feita localmente com regras simples ou futuramente com IA.

---

## 9.3 Capitalização automática

Melhorar início de frase:

```txt
olá estou testando
```

Virar:

```txt
Olá estou testando.
```

---

## 9.4 Dicionário personalizado

Permitir configurar palavras que o Whisper costuma errar.

Exemplo:

```json
{
  "replacements": {
    "VS Gold": "VS Code",
    "IRIUM": "Iriun",
    "Gite Rob": "GitHub",
    "uísper": "Whisper",
    "baixar": "Baileys"
  }
}
```

Vantagens:

* Corrigir nomes próprios.
* Corrigir termos técnicos.
* Corrigir nomes de projetos.
* Corrigir palavras recorrentes.

---

## 9.5 Modo “sem colar automaticamente”

Adicionar opção:

```txt
Transcrever, mas não colar
```

Fluxo:

```txt
Grava > transcreve > mostra no widget > usuário decide copiar/colar
```

Vantagens:

* Evita colar texto no lugar errado.
* Útil para testes.
* Útil em reuniões ou chamadas.

Configuração:

```json
{
  "auto_paste": true
}
```

---

## 9.6 Modo “confirmar antes de colar”

Fluxo:

```txt
Grava > transcreve > mostra prévia > botão Colar
```

Vantagens:

* Mais seguro.
* Evita colar texto errado.
* Útil para mensagens profissionais.

---

## 9.7 Comandos de voz

Adicionar comandos especiais falados.

Exemplos:

```txt
nova linha
ponto final
vírgula
apagar último
copiar texto
cancelar ditado
```

Exemplo:

Fala:

```txt
Olá Kennedy nova linha vamos começar o projeto ponto final
```

Resultado:

```txt
Olá Kennedy
Vamos começar o projeto.
```

---

# 10. Melhorias de segurança e estabilidade

## 10.1 Evitar abrir duas instâncias do widget

Se o usuário clicar duas vezes no atalho, pode abrir mais de um widget.

Melhoria:

Impedir múltiplas instâncias.

Comportamento ideal:

```txt
Se já estiver aberto, apenas trazer a janela existente para frente.
```

---

## 10.2 Tratamento melhor de erro de microfone

Se o Iriun não estiver aberto ou conectado, mostrar mensagem clara:

```txt
Microfone Iriun não encontrado.
Verifique se o Iriun Webcam está aberto no celular e no computador.
```

E oferecer:

```txt
Selecionar outro microfone
Tentar novamente
Abrir configurações
```

---

## 10.3 Verificação de arquivos obrigatórios

Ao iniciar, o app deve conferir:

```txt
whisper-cli.exe existe?
ggml-medium.bin existe?
pasta de gravações existe?
microfone existe?
bibliotecas Python estão instaladas?
```

Se algo faltar, mostrar erro amigável.

---

## 10.4 Logs técnicos

Criar arquivo:

```txt
logs/ditado_f8.log
```

Registrar:

* Quando abriu o app.
* Quando começou gravação.
* Quando terminou gravação.
* Caminho do áudio salvo.
* Tempo de transcrição.
* Erros.
* Modelo usado.
* Microfone usado.

Vantagens:

* Facilita manutenção.
* Ajuda a entender travamentos.
* Ajuda em suporte futuro.

---

## 10.5 Proteção contra gravação muito curta

Se a gravação tiver menos de, por exemplo, 0.3 segundos, descartar.

Motivo:

Evitar acionamentos acidentais.

---

## 10.6 Proteção contra gravação longa demais

Definir limite máximo:

```txt
5 minutos
```

Se passar disso:

```txt
Parar automaticamente > transcrever > avisar usuário
```

Configuração:

```json
{
  "max_recording_seconds": 300
}
```

---

# 11. Melhorias de integração com Windows

## 11.1 Iniciar com o Windows

Adicionar opção:

```txt
Iniciar automaticamente com o Windows
```

Pode ser feito criando atalho na pasta Startup:

```txt
shell:startup
```

Vantagens:

* O usuário liga o PC e o ditado já está disponível.
* Mais parecido com app real.

---

## 11.2 Rodar na bandeja do sistema

Adicionar ícone perto do relógio do Windows.

Menu da bandeja:

```txt
Abrir widget
Pausar F8
Configurações
Sair
```

Vantagens:

* Mais profissional.
* Menos poluição visual.
* Melhor controle.

---

## 11.3 Notificações do Windows

Mostrar notificações pequenas:

```txt
Texto transcrito e copiado
Erro ao encontrar microfone
Ditado cancelado
```

---

## 11.4 Instalador

Criar instalador `.exe` no futuro.

Exemplo:

```txt
DitadoF8WhisperSetup.exe
```

Poderia:

* Copiar arquivos para pasta correta.
* Criar atalho na área de trabalho.
* Criar entrada no menu iniciar.
* Configurar inicialização automática opcional.
* Instalar dependências necessárias.

---

## 11.5 Empacotar com PyInstaller

Transformar o Python em executável:

```txt
DitadoF8Whisper.exe
```

Vantagens:

* Não precisa abrir Python manualmente.
* Aparência mais profissional.
* Mais fácil levar para outro computador.

Atenção:

O Whisper e o modelo ainda precisam estar disponíveis localmente.

---

# 12. Melhorias de performance

## 12.1 Medir tempo de transcrição

Mostrar:

```txt
Transcrito em 1.8s
```

Vantagens:

* Ajuda a comparar modelos.
* Ajuda a medir desempenho.
* Ajuda a escolher entre small/medium/large.

---

## 12.2 Opção de modelo rápido

Adicionar perfil:

```txt
Rápido
Equilibrado
Qualidade
```

Exemplo:

```txt
Rápido = small
Equilibrado = medium
Qualidade = large
```

---

## 12.3 Pré-carregamento ou processo persistente

Hoje o `whisper-cli.exe` é chamado a cada transcrição.

No futuro, investigar uma forma de manter um processo mais quente ou usar integração mais direta.

Objetivo:

* Reduzir tempo de espera.
* Melhorar experiência.

---

# 13. Melhorias para uso em projetos

Como o usuário pretende usar o Ditado F8 Whisper para ajudar em outros projetos, algumas features são especialmente úteis.

## 13.1 Modo “Prompt para IA”

Adicionar opção que melhora o texto ditado para virar prompt.

Exemplo:

Texto falado:

```txt
quero que você redija um prompt para a outra ia corrigir o bug do widget
```

Saída formatada:

```txt
Redija um prompt técnico para outra IA corrigir o bug do widget. O objetivo é manter a implementação segura, preservar as funcionalidades atuais e evitar alterações desnecessárias.
```

---

## 13.2 Modo “Anotação técnica”

Formatar como nota:

```md
## Anotação

- Ideia principal:
- Problema:
- Próxima ação:
```

---

## 13.3 Modo “Comando PowerShell”

Quando o usuário ditar comandos, não corrigir demais.

Exemplo:

```txt
cd c dois pontos barra whispercpp
```

Poderia tentar transformar em:

```powershell
cd "C:\whispercpp"
```

Essa feature deve ser tratada com cuidado.

---

## 13.4 Modo “Documentação”

Transformar ditado em texto mais limpo, com títulos e tópicos.

---

# 14. Melhorias de privacidade

## 14.1 Aviso claro de processamento local

Mostrar no README e talvez no app:

```txt
Transcrição local usando Whisper.
Os áudios ficam salvos apenas neste computador.
```

---

## 14.2 Modo não salvar áudio

Adicionar opção:

```json
{
  "save_audio": false
}
```

Uso:

Depois que o sistema estiver homologado, o usuário pode preferir não salvar todos os áudios.

---

## 14.3 Modo não salvar texto

Adicionar opção:

```json
{
  "save_txt": false
}
```

Uso:

Mais privacidade.

---

## 14.4 Modo privado temporário

Botão:

```txt
Modo privado
```

Nesse modo:

* Transcreve.
* Cola.
* Não salva áudio.
* Não salva TXT.
* Não registra histórico.

---

# 15. Organização sugerida das próximas fases

## Fase 1 — Configuração básica

Implementar:

* `config.json`.
* Troca de tecla.
* Escolha entre modo `hold` e `toggle`.
* Cancelar gravação com `Esc`.
* Melhor tratamento de erros.

Prioridade: alta.

---

## Fase 2 — Melhorias de usabilidade

Implementar:

* Contador de tempo.
* Modo compacto.
* Modo expandido.
* Botão de gravar no widget.
* Copiar último texto por atalho.
* Repetir última colagem.

Prioridade: alta.

---

## Fase 3 — Histórico

Implementar:

* Organização por data.
* Arquivo `.json` por ditado.
* Lista dos últimos ditados.
* Busca simples.
* Favoritos.
* Exportação.

Prioridade: média.

---

## Fase 4 — Design profissional

Implementar:

* Tema refinado.
* Tema claro/escuro.
* Animações leves.
* Indicador de volume.
* Melhor layout dos botões.
* Ícone na bandeja do Windows.

Prioridade: média.

---

## Fase 5 — Produto real para Windows

Implementar:

* Iniciar com Windows.
* Rodar na bandeja.
* Empacotar com PyInstaller.
* Criar instalador.
* Criar página de ajuda.
* Criar release no GitHub.

Prioridade: futura.

---

# 16. Features prioritárias escolhidas para a próxima implementação

As próximas melhorias mais importantes são:

## 16.1 Criar `config.json`

Para deixar configurável:

* Tecla principal.
* Modo de gravação.
* Microfone.
* Modelo.
* Pasta de saída.
* Colagem automática.
* Salvamento de áudio.
* Salvamento de TXT.

---

## 16.2 Permitir trocar a tecla F8

O usuário deve poder trocar o botão de ditado sem mexer diretamente no código.

---

## 16.3 Adicionar modo toggle

Além do modo atual de segurar F8, adicionar:

```txt
Apertar F8 para iniciar
Apertar F8 novamente para parar
```

---

## 16.4 Melhorar design

Deixar o widget mais profissional, com:

* Modo compacto.
* Melhor alinhamento.
* Melhor visual dos botões.
* Status mais chamativos.
* Contador de gravação.
* Talvez indicador de volume.

---

# 17. Conclusão

O Ditado F8 Whisper já está útil para uso real no dia a dia. A principal vantagem é permitir escrever em qualquer lugar do Windows apenas falando, com privacidade e sem depender de serviços online.

A evolução natural agora é transformar o projeto em uma ferramenta configurável e profissional, mantendo a simplicidade do fluxo principal:

```txt
Apertar botão > falar > receber texto pronto
```

As melhorias mais importantes para a próxima versão são:

1. Permitir trocar a tecla F8.
2. Permitir escolher entre modo segurar e modo liga/desliga.
3. Criar arquivo `config.json`.
4. Melhorar ainda mais o design.
5. Adicionar contador e feedback visual mais forte.
6. Preparar o app para uso diário contínuo.
