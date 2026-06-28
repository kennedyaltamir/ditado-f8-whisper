# Ditado F8 Whisper

Mini app local para Windows que transforma voz em texto usando Whisper local.

## Função principal

Segurar F8 > falar > soltar F8 > transcrever > colar texto no campo ativo.

## Status

- Widget visual premium
- Microfone Iriun selecionado automaticamente
- Salva áudio `.wav`
- Salva transcrição `.txt`
- Mostra último texto reconhecido
- Botões para abrir pasta, ouvir áudio, abrir TXT e copiar texto
- Roda localmente no Windows

## Requisitos

- Windows 11
- Python 3.10+
- whisper.cpp baixado localmente
- Modelo `ggml-medium.bin`
- Bibliotecas Python:
  - keyboard
  - numpy
  - pyperclip
  - sounddevice

## Instalação das bibliotecas

```powershell
python -m pip install sounddevice numpy pyperclip keyboard
Arquivos principais
ditado_f8_widget.py — widget principal
ditado_f8.py — versão simples antiga
Iniciar Ditado F8 Widget.vbs — abre o widget sem terminal
Iniciar Ditado F8.bat — versão antiga via terminal
Ditado_F8_Whisper.ico — ícone do projeto
Observação
