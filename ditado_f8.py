import os
import re
import wave
import time
import subprocess
import tempfile

import keyboard
import numpy as np
import pyperclip
import sounddevice as sd


WHISPER_DIR = r"C:\whispercpp\whisper-bin-x64\Release"
WHISPER_EXE = os.path.join(WHISPER_DIR, "whisper-cli.exe")
MODEL_PATH = os.path.join(WHISPER_DIR, "models", "ggml-medium.bin")

SAMPLE_RATE = 16000
CHANNELS = 1

HOTKEY = "f8"
MIC_NAME_CONTAINS = "Iriun"


def find_input_device():
    devices = sd.query_devices()

    for index, device in enumerate(devices):
        name = device.get("name", "")
        max_input_channels = device.get("max_input_channels", 0)

        if MIC_NAME_CONTAINS.lower() in name.lower() and max_input_channels > 0:
            print(f"Microfone selecionado: #{index} - {name}")
            return index

    print("Não encontrei o microfone Iriun automaticamente.")
    print("Dispositivos de entrada encontrados:")

    for index, device in enumerate(devices):
        if device.get("max_input_channels", 0) > 0:
            print(f"#{index} - {device.get('name')}")

    raise RuntimeError("Microfone Iriun não encontrado.")


def save_wav(path, audio_data):
    audio_int16 = np.int16(audio_data * 32767)

    with wave.open(path, "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(audio_int16.tobytes())


def transcribe_wav(path):
    command = [
        WHISPER_EXE,
        "-m", MODEL_PATH,
        "-l", "pt",
        "-f", path,
    ]

    result = subprocess.run(
        command,
        cwd=WHISPER_DIR,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    output = result.stdout + "\n" + result.stderr

    lines = []
    for line in output.splitlines():
        match = re.search(r"\]\s+(.*)$", line)
        if match:
            text = match.group(1).strip()
            if text and not text.startswith("["):
                lines.append(text)

    final_text = " ".join(lines).strip()

    final_text = re.sub(r"\s+", " ", final_text)
    final_text = final_text.replace("[Música]", "").replace("[Silêncio]", "").strip()

    return final_text


def record_until_release(device_index):
    print("Gravando... solte F8 para transcrever.")

    frames = []

    def callback(indata, frames_count, time_info, status):
        if status:
            print(status)
        frames.append(indata.copy())

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="float32",
        device=device_index,
        callback=callback,
    ):
        while keyboard.is_pressed(HOTKEY):
            time.sleep(0.05)

    if not frames:
        return None

    return np.concatenate(frames, axis=0)


def main():
    print("Ditado F8 iniciado.")
    print("Segure F8, fale, solte F8 para colar o texto no campo ativo.")
    print("Para sair, feche esta janela.")
    print()

    device_index = find_input_device()

    while True:
        keyboard.wait(HOTKEY)

        audio_data = record_until_release(device_index)
        if audio_data is None:
            continue

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            wav_path = temp_file.name

        try:
            save_wav(wav_path, audio_data)

            print("Transcrevendo...")
            text = transcribe_wav(wav_path)

            if not text:
                print("Nenhum texto reconhecido.")
                continue

            print(f"Texto reconhecido: {text}")

            pyperclip.copy(text)
            keyboard.press_and_release("ctrl+v")

            print("Texto colado.")
            print()

        finally:
            try:
                os.remove(wav_path)
            except OSError:
                pass


if __name__ == "__main__":
    main()