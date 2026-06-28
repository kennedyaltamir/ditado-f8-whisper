import os
import re
import wave
import time
import tempfile
import threading
import subprocess
import tkinter as tk
from datetime import datetime

import keyboard
import numpy as np
import pyperclip
import sounddevice as sd
import winsound


WHISPER_DIR = r"C:\whispercpp\whisper-bin-x64\Release"
WHISPER_EXE = os.path.join(WHISPER_DIR, "whisper-cli.exe")
MODEL_PATH = os.path.join(WHISPER_DIR, "models", "ggml-medium.bin")

SAVE_DIR = r"C:\whispercpp\gravacoes_ditado"

SAMPLE_RATE = 16000
CHANNELS = 1
HOTKEY = "f8"
MIC_NAME_CONTAINS = "Iriun"


class DitadoWidget:
    def __init__(self, root):
        os.makedirs(SAVE_DIR, exist_ok=True)

        self.root = root
        self.root.title("Ditado F8 Whisper")
        self.root.geometry("500x260+1300+80")
        self.root.configure(bg="#111111")
        self.root.attributes("-topmost", True)
        self.root.resizable(False, False)

        self.device_index = self.find_input_device()

        self.is_recording = False
        self.is_processing = False
        self.frames = []
        self.stream = None

        self.status_var = tk.StringVar(value="Pronto")
        self.detail_var = tk.StringVar(value="Segure F8 para ditar")
        self.last_text_var = tk.StringVar(value="Último texto: nenhum")
        self.last_file_var = tk.StringVar(value="Último áudio: nenhum")

        self.build_ui()
        self.register_hotkeys()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def build_ui(self):
        top = tk.Frame(self.root, bg="#111111")
        top.pack(fill="x", padx=10, pady=(10, 5))

        title = tk.Label(
            top,
            text="🎤 Ditado F8 Whisper",
            fg="white",
            bg="#111111",
            font=("Segoe UI", 12, "bold")
        )
        title.pack(side="left")

        close_btn = tk.Button(
            top,
            text="X",
            command=self.on_close,
            bg="#222222",
            fg="white",
            activebackground="#444444",
            activeforeground="white",
            relief="flat",
            width=3
        )
        close_btn.pack(side="right")

        self.status_label = tk.Label(
            self.root,
            textvariable=self.status_var,
            fg="#00d26a",
            bg="#111111",
            font=("Segoe UI", 18, "bold")
        )
        self.status_label.pack(anchor="w", padx=14, pady=(8, 0))

        self.detail_label = tk.Label(
            self.root,
            textvariable=self.detail_var,
            fg="#cccccc",
            bg="#111111",
            font=("Segoe UI", 10)
        )
        self.detail_label.pack(anchor="w", padx=14, pady=(6, 0))

        self.last_text_label = tk.Label(
            self.root,
            textvariable=self.last_text_var,
            fg="#9fd3ff",
            bg="#111111",
            font=("Segoe UI", 9),
            justify="left",
            wraplength=460
        )
        self.last_text_label.pack(anchor="w", padx=14, pady=(12, 0))

        self.last_file_label = tk.Label(
            self.root,
            textvariable=self.last_file_var,
            fg="#aaaaaa",
            bg="#111111",
            font=("Segoe UI", 8),
            justify="left",
            wraplength=460
        )
        self.last_file_label.pack(anchor="w", padx=14, pady=(8, 0))

        btn_frame = tk.Frame(self.root, bg="#111111")
        btn_frame.pack(fill="x", padx=14, pady=(12, 0))

        open_folder_btn = tk.Button(
            btn_frame,
            text="Abrir pasta dos testes",
            command=self.open_save_folder,
            bg="#1f6feb",
            fg="white",
            activebackground="#388bfd",
            activeforeground="white",
            relief="flat",
            padx=10,
            pady=5
        )
        open_folder_btn.pack(side="left")

    def register_hotkeys(self):
        keyboard.on_press_key(HOTKEY, self.on_f8_press)
        keyboard.on_release_key(HOTKEY, self.on_f8_release)

    def find_input_device(self):
        devices = sd.query_devices()

        for index, device in enumerate(devices):
            name = device.get("name", "")
            max_input_channels = device.get("max_input_channels", 0)

            if MIC_NAME_CONTAINS.lower() in name.lower() and max_input_channels > 0:
                return index

        raise RuntimeError("Microfone Iriun não encontrado.")

    def set_status(self, status, detail="", color="#00d26a"):
        def update():
            self.status_var.set(status)
            self.detail_var.set(detail)
            self.status_label.config(fg=color)

        self.root.after(0, update)

    def set_last_text(self, text):
        if not text:
            text = "nenhum"

        preview = text if len(text) <= 260 else text[:260] + "..."
        self.root.after(0, lambda: self.last_text_var.set(f"Último texto: {preview}"))

    def set_last_file(self, wav_path, txt_path):
        wav_name = os.path.basename(wav_path)
        txt_name = os.path.basename(txt_path)
        msg = f"Áudio salvo: {wav_name} | Texto salvo: {txt_name}"
        self.root.after(0, lambda: self.last_file_var.set(msg))

    def open_save_folder(self):
        os.makedirs(SAVE_DIR, exist_ok=True)
        os.startfile(SAVE_DIR)

    def beep_start(self):
        try:
            winsound.Beep(1000, 120)
        except Exception:
            pass

    def beep_end(self):
        try:
            winsound.Beep(700, 120)
        except Exception:
            pass

    def beep_error(self):
        try:
            winsound.Beep(400, 180)
        except Exception:
            pass

    def on_f8_press(self, event):
        if self.is_recording or self.is_processing:
            return

        self.is_recording = True
        self.frames = []

        self.set_status("Gravando...", "Solte F8 para transcrever", "#ff5252")
        self.beep_start()

        def callback(indata, frames_count, time_info, status):
            if self.is_recording:
                self.frames.append(indata.copy())

        try:
            self.stream = sd.InputStream(
                samplerate=SAMPLE_RATE,
                channels=CHANNELS,
                dtype="float32",
                device=self.device_index,
                callback=callback,
            )
            self.stream.start()

        except Exception as e:
            self.is_recording = False
            self.stream = None
            self.set_status("Erro", str(e), "#ff4444")
            self.beep_error()

    def on_f8_release(self, event):
        if not self.is_recording:
            return

        self.is_recording = False

        try:
            if self.stream is not None:
                self.stream.stop()
                self.stream.close()
                self.stream = None
        except Exception:
            pass

        if not self.frames:
            self.set_status("Pronto", "Segure F8 para ditar", "#00d26a")
            return

        audio_data = np.concatenate(self.frames, axis=0)

        self.is_processing = True
        self.set_status("Carregando sua voz...", "Transcrevendo, salvando e colando", "#ffd166")
        self.beep_end()

        threading.Thread(target=self.process_audio, args=(audio_data,), daemon=True).start()

    def save_wav(self, path, audio_data):
        audio_int16 = np.int16(audio_data * 32767)

        with wave.open(path, "wb") as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(2)
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(audio_int16.tobytes())

    def transcribe_wav(self, path):
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

                if not text:
                    continue

                if text.startswith("[") and text.endswith("]"):
                    continue

                lines.append(text)

        final_text = " ".join(lines).strip()
        final_text = re.sub(r"\s+", " ", final_text)

        return final_text

    def save_txt(self, path, text):
        with open(path, "w", encoding="utf-8") as f:
            f.write(text.strip() + "\n")

    def process_audio(self, audio_data):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        wav_path = os.path.join(SAVE_DIR, f"{timestamp}.wav")
        txt_path = os.path.join(SAVE_DIR, f"{timestamp}.txt")

        try:
            self.save_wav(wav_path, audio_data)

            text = self.transcribe_wav(wav_path)

            if not text:
                text = ""

            self.save_txt(txt_path, text)
            self.set_last_file(wav_path, txt_path)

            if not text:
                self.set_status("Sem texto", "Áudio salvo, mas nada foi reconhecido", "#ffaa00")
                self.set_last_text("nenhum")
                time.sleep(1.5)
                self.set_status("Pronto", "Segure F8 para ditar", "#00d26a")
                return

            self.set_last_text(text)

            pyperclip.copy(text)
            time.sleep(0.1)
            keyboard.press_and_release("ctrl+v")

            self.set_status("Texto colado", "Áudio e transcrição salvos", "#00d26a")
            time.sleep(1.2)
            self.set_status("Pronto", "Segure F8 para ditar", "#00d26a")

        except Exception as e:
            self.set_status("Erro", str(e), "#ff4444")
            self.beep_error()

        finally:
            self.is_processing = False

    def on_close(self):
        try:
            keyboard.unhook_all()
        except Exception:
            pass

        self.root.destroy()


def main():
    root = tk.Tk()
    app = DitadoWidget(root)
    root.mainloop()


if __name__ == "__main__":
    main()