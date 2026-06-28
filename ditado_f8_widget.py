import os
import re
import wave
import time
import json
import threading
import subprocess
import tkinter as tk
from datetime import datetime

import keyboard
import numpy as np
import pyperclip
import sounddevice as sd
import winsound


# ==========================================================
# Configurações Padrão e Caminhos Seguros
# ==========================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")

DEFAULT_CONFIG = {
    "hotkey": "f8",
    "cancel_hotkey": "esc",
    "recording_mode": "hold",
    "microphone_name_contains": "Iriun",
    "whisper_dir": r"C:\whispercpp\whisper-bin-x64\Release",
    "whisper_exe": r"C:\whispercpp\whisper-bin-x64\Release\whisper-cli.exe",
    "model_path": r"C:\whispercpp\whisper-bin-x64\Release\models\ggml-medium.bin",
    "save_dir": r"C:\whispercpp\gravacoes_ditado",
    "language": "pt",
    "sample_rate": 16000,
    "channels": 1,
    "auto_paste": True,
    "save_audio": True,
    "save_txt": True,
    "always_on_top": True
}

def load_config():
    if not os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_CONFIG, f, indent=2, ensure_ascii=False)
        except Exception:
            pass
        return DEFAULT_CONFIG.copy()

    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            user_config = json.load(f)
        
        config = DEFAULT_CONFIG.copy()
        config.update(user_config)
        return config
    except Exception:
        return DEFAULT_CONFIG.copy()

# ==========================================================
# Constantes Visuais
# ==========================================================
ICON_PATH = os.path.join(BASE_DIR, "Ditado_F8_Whisper.ico")

BG_TRANSPARENT = "#010101"
BG_CARD = "#10151f"
BG_CARD_2 = "#151c29"
BG_BUTTON = "#1f6feb"
BG_BUTTON_HOVER = "#388bfd"

COLOR_READY = "#00d26a"
COLOR_RECORDING = "#ff4d5e"
COLOR_PROCESSING = "#ffd166"
COLOR_SUCCESS = "#00d26a"
COLOR_ERROR = "#ff4444"
COLOR_TEXT = "#dbeafe"
COLOR_MUTED = "#9aa4b2"
COLOR_BLUE = "#7dd3fc"


class DitadoWidget:
    def __init__(self, root):
        self.config = load_config()
        self.save_dir = self.config.get("save_dir", r"C:\whispercpp\gravacoes_ditado")
        os.makedirs(self.save_dir, exist_ok=True)

        self.root = root
        self.root.title("Ditado F8 Whisper")
        self.root.geometry("560x330+1280+80")
        self.root.configure(bg=BG_TRANSPARENT)
        self.root.attributes("-topmost", self.config.get("always_on_top", True))
        self.root.resizable(False, False)

        # Janela sem borda
        self.root.overrideredirect(True)

        # Tenta deixar os cantos transparentes no Windows
        try:
            self.root.wm_attributes("-transparentcolor", BG_TRANSPARENT)
        except Exception:
            pass

        # Ícone, quando aplicável
        try:
            if os.path.exists(ICON_PATH):
                self.root.iconbitmap(ICON_PATH)
        except Exception:
            pass

        self.hotkey = self.config.get("hotkey", "f8").lower()
        self.cancel_hotkey = self.config.get("cancel_hotkey", "esc").lower()
        self.recording_mode = self.config.get("recording_mode", "hold")
        
        mode_str = "Segurar" if self.recording_mode == "hold" else "Toggle"
        self.ready_text = f"Rodando em segundo plano • Hotkey: {self.hotkey.upper()} • Modo: {mode_str}"

        self.status_var = tk.StringVar(value="Pronto")
        self.detail_var = tk.StringVar(value=self.ready_text)
        self.last_text_var = tk.StringVar(value="Último texto: nenhum")
        self.last_file_var = tk.StringVar(value="Nenhum teste salvo ainda")
        
        mic_name = self.config.get("microphone_name_contains", "Iriun")
        self.mic_var = tk.StringVar(value=f"Microfone: {mic_name}")

        self.device_index = self.find_input_device()

        # Variáveis de Estado
        self.is_recording = False
        self.is_processing = False
        self.is_hotkey_pressed = False
        self.cancel_until_hotkey_released = False
        self.frames = []
        self.stream = None

        self.last_text = ""
        self.last_wav_path = ""
        self.last_txt_path = ""

        self.drag_start_x = 0
        self.drag_start_y = 0

        self.build_ui()
        self.register_hotkeys()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.bind("<Map>", self.on_restore)

    # ==========================================================
    # UI
    # ==========================================================

    def build_ui(self):
        self.canvas = tk.Canvas(
            self.root,
            width=560,
            height=330,
            bg=BG_TRANSPARENT,
            highlightthickness=0,
            bd=0
        )
        self.canvas.pack(fill="both", expand=True)

        self.draw_rounded_card()

        self.card = tk.Frame(self.root, bg=BG_CARD)
        self.card.place(x=14, y=14, width=532, height=302)

        self.build_header()
        self.build_status_area()
        self.build_last_text_area()
        self.build_buttons()

    def draw_rounded_card(self):
        self.round_rectangle(10, 10, 550, 322, radius=24, fill="#05070c", outline="")
        self.round_rectangle(14, 14, 546, 318, radius=22, fill=BG_CARD, outline="#263244")
        self.round_rectangle(14, 14, 546, 82, radius=22, fill=BG_CARD_2, outline="")
        self.canvas.create_rectangle(14, 58, 546, 82, fill=BG_CARD_2, outline="")

    def round_rectangle(self, x1, y1, x2, y2, radius=25, **kwargs):
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1,
        ]
        return self.canvas.create_polygon(points, smooth=True, **kwargs)

    def build_header(self):
        self.header = tk.Frame(self.card, bg=BG_CARD_2, height=58)
        self.header.pack(fill="x")

        self.header.bind("<Button-1>", self.start_drag)
        self.header.bind("<B1-Motion>", self.do_drag)

        title_frame = tk.Frame(self.header, bg=BG_CARD_2)
        title_frame.pack(side="left", padx=16, pady=10)

        title = tk.Label(
            title_frame,
            text="🎤 Ditado F8 Whisper",
            fg="white",
            bg=BG_CARD_2,
            font=("Segoe UI", 13, "bold")
        )
        title.pack(anchor="w")

        subtitle = tk.Label(
            title_frame,
            textvariable=self.mic_var,
            fg=COLOR_MUTED,
            bg=BG_CARD_2,
            font=("Segoe UI", 8)
        )
        subtitle.pack(anchor="w")

        controls = tk.Frame(self.header, bg=BG_CARD_2)
        controls.pack(side="right", padx=10, pady=10)

        min_btn = self.make_window_button(controls, "—", self.minimize_window)
        min_btn.pack(side="left", padx=(0, 6))

        close_btn = self.make_window_button(controls, "X", self.on_close, danger=True)
        close_btn.pack(side="left")

    def make_window_button(self, parent, text, command, danger=False):
        bg = "#202938"
        hover = "#334155"
        fg = "white"
        if danger:
            bg = "#2a1f25"
            hover = "#7f1d1d"

        btn = tk.Button(
            parent, text=text, command=command, bg=bg, fg=fg,
            activebackground=hover, activeforeground="white",
            relief="flat", width=4, height=1, font=("Segoe UI", 10, "bold"), cursor="hand2"
        )
        btn.bind("<Enter>", lambda e: btn.config(bg=hover))
        btn.bind("<Leave>", lambda e: btn.config(bg=bg))
        return btn

    def build_status_area(self):
        body = tk.Frame(self.card, bg=BG_CARD)
        body.pack(fill="x", padx=18, pady=(18, 0))

        self.status_dot = tk.Canvas(body, width=18, height=18, bg=BG_CARD, highlightthickness=0)
        self.status_dot.pack(side="left", anchor="n", pady=(8, 0))
        self.status_dot_id = self.status_dot.create_oval(3, 3, 15, 15, fill=COLOR_READY, outline="")

        status_text_frame = tk.Frame(body, bg=BG_CARD)
        status_text_frame.pack(side="left", fill="x", expand=True, padx=(10, 0))

        self.status_label = tk.Label(
            status_text_frame, textvariable=self.status_var, fg=COLOR_READY,
            bg=BG_CARD, font=("Segoe UI", 22, "bold")
        )
        self.status_label.pack(anchor="w")

        self.detail_label = tk.Label(
            status_text_frame, textvariable=self.detail_var, fg=COLOR_MUTED,
            bg=BG_CARD, font=("Segoe UI", 10)
        )
        self.detail_label.pack(anchor="w", pady=(2, 0))

    def build_last_text_area(self):
        area = tk.Frame(self.card, bg=BG_CARD)
        area.pack(fill="x", padx=18, pady=(18, 0))

        self.last_text_label = tk.Label(
            area, textvariable=self.last_text_var, fg=COLOR_BLUE, bg=BG_CARD,
            font=("Segoe UI", 9), justify="left", anchor="w", wraplength=500
        )
        self.last_text_label.pack(anchor="w", fill="x")

        self.last_file_label = tk.Label(
            area, textvariable=self.last_file_var, fg=COLOR_MUTED, bg=BG_CARD,
            font=("Segoe UI", 8), justify="left", anchor="w", wraplength=500
        )
        self.last_file_label.pack(anchor="w", fill="x", pady=(8, 0))

    def build_buttons(self):
        btn_frame = tk.Frame(self.card, bg=BG_CARD)
        btn_frame.pack(fill="x", padx=18, pady=(18, 0))

        self.make_action_button(btn_frame, "Abrir pasta", self.open_save_folder).pack(side="left", padx=(0, 8))
        self.make_action_button(btn_frame, "Ouvir áudio", self.open_last_audio).pack(side="left", padx=(0, 8))
        self.make_action_button(btn_frame, "Abrir TXT", self.open_last_txt).pack(side="left", padx=(0, 8))
        self.make_action_button(btn_frame, "Copiar texto", self.copy_last_text).pack(side="left")

    def make_action_button(self, parent, text, command):
        btn = tk.Button(
            parent, text=text, command=command, bg=BG_BUTTON, fg="white",
            activebackground=BG_BUTTON_HOVER, activeforeground="white",
            relief="flat", padx=12, pady=7, font=("Segoe UI", 9, "bold"), cursor="hand2"
        )
        btn.bind("<Enter>", lambda e: btn.config(bg=BG_BUTTON_HOVER))
        btn.bind("<Leave>", lambda e: btn.config(bg=BG_BUTTON))
        return btn

    # ==========================================================
    # Janela
    # ==========================================================

    def start_drag(self, event):
        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def do_drag(self, event):
        x = self.root.winfo_pointerx() - self.drag_start_x
        y = self.root.winfo_pointery() - self.drag_start_y
        self.root.geometry(f"+{x}+{y}")

    def minimize_window(self):
        try:
            self.root.overrideredirect(False)
            self.root.iconify()
        except Exception:
            pass

    def on_restore(self, event=None):
        try:
            if self.root.state() == "normal":
                self.root.after(50, lambda: self.root.overrideredirect(True))
        except Exception:
            pass

    # ==========================================================
    # Microfone
    # ==========================================================

    def find_input_device(self):
        devices = sd.query_devices()
        mic_name_contains = self.config.get("microphone_name_contains", "Iriun").lower()

        for index, device in enumerate(devices):
            name = device.get("name", "")
            max_input_channels = device.get("max_input_channels", 0)

            if mic_name_contains in name.lower() and max_input_channels > 0:
                if hasattr(self, "mic_var"):
                    self.mic_var.set(f"Microfone: #{index} - {name}")
                return index

        raise RuntimeError(f"Microfone '{mic_name_contains}' não encontrado.")

    # ==========================================================
    # Hotkey (Captura Global)
    # ==========================================================

    def register_hotkeys(self):
        try:
            keyboard.unhook_all()
        except Exception:
            pass

        keyboard.hook(self.on_key_event)

    def on_key_event(self, event):
        if self.is_processing:
            return

        try:
            cancel_pressed = keyboard.is_pressed(self.cancel_hotkey)
            hotkey_pressed = keyboard.is_pressed(self.hotkey)
        except Exception:
            return

        # 1. Tratamento do Cancelamento
        if cancel_pressed:
            if self.is_recording:
                # Aciona a trava: impede retomada imediata da gravação se a hotkey ainda estiver segurada
                self.cancel_until_hotkey_released = True
                self.cancel_recording()
            return

        # 2. Liberação da trava de cancelamento ao soltar a hotkey principal
        if not hotkey_pressed:
            self.cancel_until_hotkey_released = False

        # 3. Tratamento da Gravação
        if self.recording_mode == "toggle":
            # Toggle mode: age no aperto inicial
            if hotkey_pressed and not self.is_hotkey_pressed:
                self.is_hotkey_pressed = True
                
                if not self.cancel_until_hotkey_released:
                    if not self.is_recording:
                        self.start_recording()
                    else:
                        self.stop_and_process()
            
            elif not hotkey_pressed:
                self.is_hotkey_pressed = False

        else: 
            # Hold mode: grava enquanto pressionado, para ao soltar
            if hotkey_pressed:
                if not self.is_recording and not self.cancel_until_hotkey_released:
                    self.start_recording()
            else:
                if self.is_recording:
                    self.stop_and_process()

    # ==========================================================
    # Status e Ações Visuais
    # ==========================================================

    def set_status(self, status, detail="", color=COLOR_READY):
        def update():
            self.status_var.set(status)
            self.detail_var.set(detail)
            self.status_label.config(fg=color)
            self.status_dot.itemconfig(self.status_dot_id, fill=color)
        self.root.after(0, update)

    def set_last_text(self, text):
        text = text if text else "nenhum"
        self.last_text = text
        preview = text if len(text) <= 230 else text[:230] + "..."
        self.root.after(0, lambda: self.last_text_var.set(f"Último texto: {preview}"))

    def set_last_file(self, wav_path, txt_path):
        self.last_wav_path = wav_path
        self.last_txt_path = txt_path
        wav_name = os.path.basename(wav_path)
        txt_name = os.path.basename(txt_path)
        msg = f"Áudio: {wav_name}  |  Texto: {txt_name}"
        self.root.after(0, lambda: self.last_file_var.set(msg))

    def open_save_folder(self):
        os.makedirs(self.save_dir, exist_ok=True)
        os.startfile(self.save_dir)

    def open_last_audio(self):
        if self.last_wav_path and os.path.exists(self.last_wav_path):
            os.startfile(self.last_wav_path)
        else:
            self.set_status("Sem áudio", "Nenhum áudio salvo ainda", "#ffaa00")

    def open_last_txt(self):
        if self.last_txt_path and os.path.exists(self.last_txt_path):
            os.startfile(self.last_txt_path)
        else:
            self.set_status("Sem TXT", "Nenhuma transcrição salva ainda", "#ffaa00")

    def copy_last_text(self):
        if self.last_text:
            pyperclip.copy(self.last_text)
            self.set_status("Texto copiado", "Último texto copiado para a área de transferência", COLOR_SUCCESS)
            self.root.after(1200, lambda: self.set_status("Pronto", self.ready_text, COLOR_READY))
        else:
            self.set_status("Sem texto", "Nenhum texto para copiar", "#ffaa00")

    # ==========================================================
    # Sons
    # ==========================================================

    def beep_start(self):
        try: winsound.Beep(1000, 100)
        except Exception: pass

    def beep_end(self):
        try: winsound.Beep(700, 100)
        except Exception: pass

    def beep_success(self):
        try: winsound.Beep(1200, 80)
        except Exception: pass

    def beep_error(self):
        try: winsound.Beep(400, 180)
        except Exception: pass

    # ==========================================================
    # Gravação e Cancelamento
    # ==========================================================

    def start_recording(self):
        if self.is_recording or self.is_processing:
            return

        self.is_recording = True
        self.frames = []

        if self.recording_mode == "hold":
            detail = f"Solte {self.hotkey.upper()} para transcrever | {self.cancel_hotkey.upper()} cancela"
        else:
            detail = f"Aperte {self.hotkey.upper()} novamente para transcrever | {self.cancel_hotkey.upper()} cancela"

        self.set_status("Gravando...", detail, COLOR_RECORDING)
        self.beep_start()

        def callback(indata, frames_count, time_info, status):
            if self.is_recording:
                self.frames.append(indata.copy())

        try:
            self.stream = sd.InputStream(
                samplerate=self.config.get("sample_rate", 16000),
                channels=self.config.get("channels", 1),
                dtype="float32",
                device=self.device_index,
                callback=callback,
            )
            self.stream.start()

        except Exception as e:
            self.is_recording = False
            self.stream = None
            self.set_status("Erro", str(e), COLOR_ERROR)
            self.beep_error()

    def stop_and_process(self):
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
            self.set_status("Pronto", self.ready_text, COLOR_READY)
            return

        audio_data = np.concatenate(self.frames, axis=0)

        self.is_processing = True
        self.set_status("Carregando sua voz...", "Transcrevendo, salvando e colando", COLOR_PROCESSING)
        self.beep_end()

        threading.Thread(
            target=self.process_audio,
            args=(audio_data,),
            daemon=True
        ).start()

    def cancel_recording(self):
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
            
        self.frames = []
        self.set_status("Cancelado", "Gravação cancelada e descartada", COLOR_ERROR)
        self.beep_error()
        
        self.root.after(1500, lambda: self.set_status("Pronto", self.ready_text, COLOR_READY))

    def save_wav(self, path, audio_data):
        audio_int16 = np.int16(audio_data * 32767)
        with wave.open(path, "wb") as wf:
            wf.setnchannels(self.config.get("channels", 1))
            wf.setsampwidth(2)
            wf.setframerate(self.config.get("sample_rate", 16000))
            wf.writeframes(audio_int16.tobytes())

    # ==========================================================
    # Transcrição e Colagem
    # ==========================================================

    def transcribe_wav(self, path):
        command = [
            self.config.get("whisper_exe", r"C:\whispercpp\whisper-bin-x64\Release\whisper-cli.exe"),
            "-m", self.config.get("model_path", r"C:\whispercpp\whisper-bin-x64\Release\models\ggml-medium.bin"),
            "-l", self.config.get("language", "pt"),
            "-f", path,
        ]

        result = subprocess.run(
            command,
            cwd=self.config.get("whisper_dir", r"C:\whispercpp\whisper-bin-x64\Release"),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        output = result.stdout + "\n" + result.stderr

        lines = []
        for line in output.splitlines():
            match = re.search(r"\]\s+(.*)$", line)
            if not match:
                continue

            text = match.group(1).strip()
            if not text:
                continue
            
            # Remove ruídos comuns do Whisper
            if text.startswith("[") and text.endswith("]"):
                continue
            if re.fullmatch(r"\[.*?\]", text):
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
        wav_path = os.path.join(self.save_dir, f"{timestamp}.wav")
        txt_path = os.path.join(self.save_dir, f"{timestamp}.txt")

        try:
            # Preservado comportamento default de salvar ambos em todos os casos nesta fase, 
            # garantindo que os botões do UI funcionem perfeitamente.
            self.save_wav(wav_path, audio_data)

            text = self.transcribe_wav(wav_path)
            if not text:
                text = ""

            self.save_txt(txt_path, text)
            self.set_last_file(wav_path, txt_path)

            if not text:
                self.set_status("Sem texto", "Áudio analisado, mas nada foi reconhecido", "#ffaa00")
                self.set_last_text("nenhum")
                time.sleep(1.5)
                self.set_status("Pronto", self.ready_text, COLOR_READY)
                return

            self.set_last_text(text)

            if self.config.get("auto_paste", True):
                pyperclip.copy(text)
                time.sleep(0.1)
                keyboard.press_and_release("ctrl+v")
                self.set_status("Texto colado", "Áudio e transcrição concluídos", COLOR_SUCCESS)
            else:
                self.set_status("Texto copiado", "Transcrição enviada à área de transferência", COLOR_SUCCESS)
                pyperclip.copy(text)
                
            self.beep_success()
            time.sleep(1.2)
            self.set_status("Pronto", self.ready_text, COLOR_READY)

        except Exception as e:
            self.set_status("Erro", str(e), COLOR_ERROR)
            self.beep_error()

        finally:
            self.is_processing = False

    # ==========================================================
    # Fechamento
    # ==========================================================

    def on_close(self):
        try:
            if self.stream is not None:
                self.stream.stop()
                self.stream.close()
        except Exception:
            pass

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
