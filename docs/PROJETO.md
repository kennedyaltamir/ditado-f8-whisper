# VISÃO GERAL DO PROJETO: DITADO F8 WHISPER

## 1. Identificação
* **Nome do Projeto:** Ditado F8 Whisper
* **Objetivo Principal:** Criar um mini aplicativo local para Windows que transforma voz em texto de forma rápida e privada, utilizando o Whisper rodando localmente na máquina, para acelerar a digitação de prompts, e-mails e comandos.
* **Público-Alvo:** O próprio criador (uso pessoal) e profissionais que buscam aumentar a produtividade usando voz em vez de digitação manual.
* **Repositório:** `https://github.com/kennedyaltamir/ditado-f8-whisper`
* **Ambiente de Desenvolvimento:** Windows 11 (Pasta base: `C:\whispercpp`)

## 2. Especificações Técnicas (Stack)
* **Linguagem:** Python
* **Bibliotecas Principais:** `tkinter` (UI), `keyboard` (hotkeys), `sounddevice` & `numpy` & `wave` (gravação de áudio), `pyperclip` (área de transferência), `subprocess` & `threading` (execução do Whisper em background), `os`, `re`, `time`, `datetime`.
* **Motor de Transcrição:** Whisper.cpp (`whisper-cli.exe`)
* **Modelo Atual:** `ggml-medium.bin` (Idioma: Português - `pt`)
* **Microfone Homologado:** Iriun Webcam

## 3. O Problema Resolvido
Digitar textos longos ou prompts complexos para outras IAs consome muito tempo e gera fadiga. Soluções online dependem de internet e expõem dados. O Ditado F8 resolve isso criando um atalho global (F8) que grava o áudio, transcreve offline via Whisper e cola automaticamente no campo onde o cursor estiver, de forma transparente e imediata.

## 4. Estado Atual (MVP Funcional)
O projeto não é mais um protótipo, é um software em uso diário. 
Atualmente, o arquivo principal é o `ditado_f8_widget.py`, que atua como um monolito integrando a interface visual premium (sem bordas), a escuta da tecla F8, a gravação de áudio e a orquestração do Whisper. O fluxo "Segurar F8 > Falar > Soltar > Transcrever > Colar" está 100% operacional. O projeto é iniciado por um script `.vbs` que roda o Python em background.

## 5. Caminhos Absolutos Homologados
Atualmente, o sistema baseia-se em caminhos absolutos locais que **estão homologados e funcionais**. Eles não devem ser tratados como erro:
* Pasta base: `C:\whispercpp`
* Executável: `C:\whispercpp\whisper-bin-x64\Release\whisper-cli.exe`
* Diretório de Gravações: `C:\whispercpp\gravacoes_ditado`
* *(No futuro, esses caminhos serão externalizados para um `config.json`, mas hoje operam nativamente dessa forma).*
