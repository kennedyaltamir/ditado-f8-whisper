import os
import re
import wave
import time
import json
import threading
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
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
BG_SETTINGS = "#0d1117"

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
        # Altura aumentada de 345 para 410 para acomodar os novos controles
        self.root.geometry("560x410+1280+80")
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
        
        self.ready_text = "Aguardando comando de voz..."

        self.status_var = tk.StringVar(value="Pronto")
        self.detail_var = tk.StringVar(value=self.ready_text)
        self.last_text_var = tk.StringVar(value="Último texto: nenhum")
        self.last_file_var = tk.StringVar(value="Nenhum teste salvo ainda")
        
        self.timer_var = tk.StringVar(value="00:00")
        self.volume_var = tk.StringVar(value="Volume: ░░░░░░░░")
        
        mic_name = self.config.get("microphone_name_contains", "Iriun")
        self.mic_var = tk.StringVar(value=f"Microfone: {mic_name}")
        
        self.badge_var = tk.StringVar()
        self.update_badge()

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
        
        self.settings_window = None
        
        # Variáveis de controle de UI (Timer e Volume)
        self.recording_start_time = 0
        self.timer_job = None
        self.volume_job = None
        self.current_volume = 0.0

        self.build_ui()
        self.register_hotkeys()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.bind("<Map>", self.on_restore)

    def update_badge(self):
        mode_str = "Segurar" if self.recording_mode == "hold" else "Toggle"
        self.badge_var.set(f"Tecla: {self.hotkey.upper()} | Modo: {mode_str}")

    # ==========================================================
    # UI Principal
    # ==========================================================

    def build_ui(self):
        self.canvas = tk.Canvas(
            self.root,
            width=560,
            height=410,
            bg=BG_TRANSPARENT,
            highlightthickness=0,
            bd=0
        )
        self.canvas.pack(fill="both", expand=True)

        self.draw_rounded_card()

        self.card = tk.Frame(self.root, bg=BG_CARD)
        self.card.place(x=14, y=14, width=532, height=382)

        self.build_header()
        self.build_status_area()
        self.build_record_controls()
        self.build_last_text_area()
        self.build_buttons()

    def draw_rounded_card(self):
        # Sombra/Borda Externa (ajustado para altura 410)
        self.round_rectangle(10, 10, 550, 400, radius=24, fill="#05070c", outline="")
        # Fundo Principal
        self.round_rectangle(14, 14, 546, 396, radius=22, fill=BG_CARD, outline="#263244")
        # Fundo do Cabeçalho
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
        
        cfg_btn = self.make_window_button(controls, "⚙", self.open_settings)
        cfg_btn.pack(side="left", padx=(0, 6))

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
        body.pack(fill="x", padx=18, pady=(15, 0))

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

        detail_container = tk.Frame(status_text_frame, bg=BG_CARD)
        detail_container.pack(anchor="w", fill="x", pady=(2, 0))

        self.detail_label = tk.Label(
            detail_container, textvariable=self.detail_var, fg=COLOR_MUTED,
            bg=BG_CARD, font=("Segoe UI", 10)
        )
        self.detail_label.pack(side="left")
        
        badge = tk.Label(
            detail_container, textvariable=self.badge_var, fg="#388bfd",
            bg="#182333", font=("Segoe UI", 8, "bold"), padx=6, pady=2
        )
        badge.pack(side="left", padx=(10, 0))

    def build_record_controls(self):
        # Painel central com Botão Gravar, Cancelar, Timer e Volume
        ctrl_frame = tk.Frame(self.card, bg="#161b26", padx=10, pady=10)
        ctrl_frame.pack(fill="x", padx=18, pady=(15, 0))
        
        # Botões à esquerda
        btn_area = tk.Frame(ctrl_frame, bg="#161b26")
        btn_area.pack(side="left")
        
        self.btn_record = tk.Button(
            btn_area, text="🎙 Gravar", command=self.toggle_recording_from_button,
            bg="#238636", fg="white", activebackground="#2ea043", activeforeground="white",
            relief="flat", font=("Segoe UI", 11, "bold"), cursor="hand2", width=12, pady=4
        )
        self.btn_record.pack(side="left", padx=(0, 8))
        
        self.btn_cancel = tk.Button(
            btn_area, text="Cancelar", command=self.cancel_recording,
            bg="#21262d", fg="#f85149", activebackground="#30363d", activeforeground="#ff7b72",
            relief="flat", font=("Segoe UI", 9, "bold"), cursor="hand2", width=8, pady=5, state="disabled"
        )
        self.btn_cancel.pack(side="left")

        # Info à direita (Timer e Volume)
        info_area = tk.Frame(ctrl_frame, bg="#161b26")
        info_area.pack(side="right", fill="y")
        
        self.lbl_timer = tk.Label(
            info_area, textvariable=self.timer_var, fg="white",
            bg="#161b26", font=("Consolas", 14, "bold")
        )
        self.lbl_timer.pack(anchor="e")
        
        self.lbl_volume = tk.Label(
            info_area, textvariable=self.volume_var, fg=COLOR_MUTED,
            bg="#161b26", font=("Consolas", 9)
        )
        self.lbl_volume.pack(anchor="e")

    def build_last_text_area(self):
        area = tk.Frame(self.card, bg=BG_CARD)
        area.pack(fill="x", padx=18, pady=(15, 0))

        self.last_text_label = tk.Label(
            area, textvariable=self.last_text_var, fg=COLOR_BLUE, bg=BG_CARD,
            font=("Segoe UI", 9), justify="left", anchor="nw", wraplength=500, height=2
        )
        self.last_text_label.pack(anchor="w", fill="x")

        self.last_file_label = tk.Label(
            area, textvariable=self.last_file_var, fg=COLOR_MUTED, bg=BG_CARD,
            font=("Segoe UI", 8), justify="left", anchor="w", wraplength=500
        )
        self.last_file_label.pack(anchor="w", fill="x", pady=(4, 0))

    def build_buttons(self):
        btn_frame = tk.Frame(self.card, bg=BG_CARD)
        btn_frame.pack(fill="x", padx=18, pady=(12, 0))

        self.make_action_button(btn_frame, "Abrir pasta", self.open_save_folder).pack(side="left", padx=(0, 8))
        self.make_action_button(btn_frame, "Ouvir áudio", self.open_last_audio).pack(side="left", padx=(0, 8))
        self.make_action_button(btn_frame, "Abrir TXT", self.open_last_txt).pack(side="left", padx=(0, 8))
        self.make_action_button(btn_frame, "Copiar texto", self.copy_last_text).pack(side="left")

    def make_action_button(self, parent, text, command):
        btn = tk.Button(
            parent, text=text, command=command, bg=BG_BUTTON, fg="white",
            activebackground=BG_BUTTON_HOVER, activeforeground="white",
            relief="flat", padx=12, pady=6, font=("Segoe UI", 9, "bold"), cursor="hand2"
        )
        btn.bind("<Enter>", lambda e: btn.config(bg=BG_BUTTON_HOVER))
        btn.bind("<Leave>", lambda e: btn.config(bg=BG_BUTTON))
        return btn

    # ==========================================================
    # Tela de Configurações (Fases 1B e 1C)
    # ==========================================================
    
    def open_settings(self):
        if self.settings_window is not None and self.settings_window.winfo_exists():
            self.settings_window.lift()
            self.settings_window.focus_force()
            return

        self.settings_window = tk.Toplevel(self.root)
        self.settings_window.title("Configurações - Ditado F8 Whisper")
        self.settings_window.geometry("450x440+1250+150")
        self.settings_window.configure(bg=BG_SETTINGS)
        self.settings_window.resizable(False, False)
        
        if self.config.get("always_on_top", True):
            self.settings_window.attributes("-topmost", True)
            
        style = ttk.Style(self.settings_window)
        style.theme_use("clam")
        
        container = tk.Frame(self.settings_window, bg=BG_SETTINGS, padx=25, pady=20)
        container.pack(fill="both", expand=True)
        
        lbl_title = tk.Label(container, text="⚙ Configurações Gerais", fg="white", bg=BG_SETTINGS, font=("Segoe UI", 14, "bold"))
        lbl_title.pack(anchor="w", pady=(0, 15))
        
        # 1. Hotkey
        frame_hotkey = tk.Frame(container, bg=BG_SETTINGS)
        frame_hotkey.pack(fill="x", pady=5)
        tk.Label(frame_hotkey, text="Tecla de ativação:", fg=COLOR_TEXT, bg=BG_SETTINGS, font=("Segoe UI", 10)).pack(side="left", anchor="w", pady=2)
        var_hotkey = tk.StringVar(value=self.hotkey)
        cb_hotkey = ttk.Combobox(frame_hotkey, textvariable=var_hotkey, values=["f6", "f7", "f8", "f9", "f10", "ctrl+space", "ctrl+alt+d"], state="normal", width=15)
        cb_hotkey.pack(side="right")
        
        # 2. Modo de Gravação
        frame_mode = tk.Frame(container, bg=BG_SETTINGS)
        frame_mode.pack(fill="x", pady=5)
        tk.Label(frame_mode, text="Modo de gravação:", fg=COLOR_TEXT, bg=BG_SETTINGS, font=("Segoe UI", 10)).pack(side="left", anchor="w", pady=2)
        
        cb_val_mode = "Segurar para falar" if self.recording_mode == "hold" else "Apertar para iniciar / parar"
        var_mode = tk.StringVar(value=cb_val_mode)
        cb_mode = ttk.Combobox(frame_mode, textvariable=var_mode, values=["Segurar para falar", "Apertar para iniciar / parar"], state="readonly", width=25)
        cb_mode.pack(side="right")

        # 3. Tecla de Cancelamento
        frame_cancel = tk.Frame(container, bg=BG_SETTINGS)
        frame_cancel.pack(fill="x", pady=5)
        tk.Label(frame_cancel, text="Tecla para cancelar:", fg=COLOR_TEXT, bg=BG_SETTINGS, font=("Segoe UI", 10)).pack(side="left", anchor="w", pady=2)
        var_cancel = tk.StringVar(value=self.cancel_hotkey)
        cb_cancel = ttk.Combobox(frame_cancel, textvariable=var_cancel, values=["esc", "f12", "ctrl+alt+c"], state="normal", width=15)
        cb_cancel.pack(side="right")
        
        tk.Frame(container, bg="#30363d", height=1).pack(fill="x", pady=15)
        
        # 4. Colar automaticamente
        var_autopaste = tk.BooleanVar(value=self.config.get("auto_paste", True))
        chk_autopaste = tk.Checkbutton(
            container, text="Colar texto automaticamente após transcrever", 
            variable=var_autopaste, fg=COLOR_TEXT, bg=BG_SETTINGS, 
            selectcolor=BG_CARD_2, activebackground=BG_SETTINGS, activeforeground="white", font=("Segoe UI", 10)
        )
        chk_autopaste.pack(anchor="w", pady=5)

        # 5. Sempre no Topo
        var_ontop = tk.BooleanVar(value=self.config.get("always_on_top", True))
        chk_ontop = tk.Checkbutton(
            container, text="Manter widget sempre no topo", 
            variable=var_ontop, fg=COLOR_TEXT, bg=BG_SETTINGS, 
            selectcolor=BG_CARD_2, activebackground=BG_SETTINGS, activeforeground="white", font=("Segoe UI", 10)
        )
        chk_ontop.pack(anchor="w", pady=5)
        
        tk.Frame(container, bg=BG_SETTINGS).pack(fill="both", expand=True)

        # Rodapé com feedback visual e botões
        frame_footer = tk.Frame(container, bg=BG_SETTINGS)
        frame_footer.pack(fill="x", side="bottom")
        
        self.lbl_feedback = tk.Label(
            frame_footer, text="As alterações são aplicadas imediatamente ao salvar.",
            fg=COLOR_MUTED, bg=BG_SETTINGS, font=("Segoe UI", 8)
        )
        self.lbl_feedback.pack(side="top", fill="x", pady=(0, 10))

        btn_actions = tk.Frame(frame_footer, bg=BG_SETTINGS)
        btn_actions.pack(fill="x")
        
        btn_open_json = tk.Button(
            btn_actions, text="Abrir config.json", command=lambda: os.startfile(CONFIG_PATH),
            bg="#21262d", fg="white", activebackground="#30363d", activeforeground="white",
            relief="flat", padx=10, pady=6, cursor="hand2"
        )
        btn_open_json.pack(side="left")

        btn_save = tk.Button(
            btn_actions, text="Salvar", 
            command=lambda: self.save_settings(
                var_hotkey.get(), var_mode.get(), var_cancel.get(), 
                var_autopaste.get(), var_ontop.get()
            ),
            bg=BG_BUTTON, fg="white", activebackground=BG_BUTTON_HOVER, activeforeground="white",
            relief="flat", padx=20, pady=6, font=("Segoe UI", 10, "bold"), cursor="hand2"
        )
        btn_save.pack(side="right")

    def show_feedback(self, msg, color):
        if hasattr(self, "lbl_feedback") and self.lbl_feedback.winfo_exists():
            self.lbl_feedback.config(text=msg, fg=color)
            
    def save_settings(self, new_hotkey, mode_str, new_cancel, auto_paste, on_top):
        if self.is_recording or self.is_processing:
            self.show_feedback("Aguarde a gravação/transcrição terminar antes de alterar configurações.", COLOR_ERROR)
            return
            
        nh = new_hotkey.strip().lower()
        nc = new_cancel.strip().lower()
        
        if not nh or not nc:
            self.show_feedback("As teclas de ativação e cancelamento não podem ficar vazias.", COLOR_ERROR)
            return
            
        if nh == nc:
            self.show_feedback("A tecla de ativação e a tecla de cancelamento não podem ser iguais.", COLOR_ERROR)
            return
            
        nm = "hold" if mode_str == "Segurar para falar" else "toggle"
        
        # 1. Atualizar JSON
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                user_config = json.load(f)
        except Exception:
            user_config = DEFAULT_CONFIG.copy()
            
        user_config["hotkey"] = nh
        user_config["recording_mode"] = nm
        user_config["cancel_hotkey"] = nc
        user_config["auto_paste"] = auto_paste
        user_config["always_on_top"] = on_top
        
        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(user_config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.show_feedback(f"Erro ao salvar config.json: {e}", COLOR_ERROR)
            return

        # 2. Atualiza a memória em tempo real
        self.hotkey = nh
        self.cancel_hotkey = nc
        self.recording_mode = nm
        self.config["auto_paste"] = auto_paste
        self.config["always_on_top"] = on_top
        
        # 3. Aplicar always_on_top visualmente
        self.root.attributes("-topmost", on_top)
        if self.settings_window and self.settings_window.winfo_exists():
            self.settings_window.attributes("-topmost", on_top)
            
        # 4. Recarregar hooks de forma segura
        self.register_hotkeys()
        
        # 5. Atualizar badge da interface
        self.update_badge()
        
        self.show_feedback("Configurações salvas e aplicadas com sucesso.", COLOR_SUCCESS)


    # ==========================================================
    # Janela Base
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
    # Hotkey (Captura Global) - Dynamic Loading
    # ==========================================================

    def unregister_hotkeys(self):
        try:
            keyboard.unhook_all()
        except Exception:
            pass

    def register_hotkeys(self):
        self.unregister_hotkeys()
        self.is_hotkey_pressed = False
        self.cancel_until_hotkey_released = False
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
        preview = text if len(text) <= 150 else text[:150] + "..."
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
    # Controle do Botão Gravar, Timer e Volume
    # ==========================================================

    def toggle_recording_from_button(self):
        if self.is_processing:
            return
        if self.is_recording:
            self.stop_and_process()
        else:
            self.start_recording()

    def update_record_button_ui(self):
        if self.is_processing:
            self.btn_record.config(text="Processando...", bg="#21262d", fg=COLOR_MUTED, state="disabled")
            self.btn_cancel.config(state="disabled")
        elif self.is_recording:
            self.btn_record.config(text="⏹ Parar", bg="#da3633", fg="white", state="normal", activebackground="#b62324")
            self.btn_cancel.config(state="normal")
        else:
            self.btn_record.config(text="🎙 Gravar", bg="#238636", fg="white", state="normal", activebackground="#2ea043")
            self.btn_cancel.config(state="disabled")

    def start_ui_loops(self):
        self.recording_start_time = time.time()
        self.update_timer()
        self.update_volume()

    def stop_ui_loops(self):
        if self.timer_job:
            self.root.after_cancel(self.timer_job)
            self.timer_job = None
        if self.volume_job:
            self.root.after_cancel(self.volume_job)
            self.volume_job = None
            
        self.timer_var.set("00:00")
        self.volume_var.set("Volume: ░░░░░░░░")
        self.current_volume = 0.0

    def update_timer(self):
        if not self.is_recording:
            return
            
        elapsed = int(time.time() - self.recording_start_time)
        mins, secs = divmod(elapsed, 60)
        self.timer_var.set(f"{mins:02d}:{secs:02d}")
        
        self.timer_job = self.root.after(1000, self.update_timer)

    def update_volume(self):
        if not self.is_recording:
            return
            
        # Mapeia o volume (RMS) para 8 níveis visuais
        # Multiplicador 20 ajusta a sensibilidade visual
        level = int(min(self.current_volume * 20, 1.0) * 8)
        bar = "█" * level + "░" * (8 - level)
        self.volume_var.set(f"Volume: {bar}")
        
        self.volume_job = self.root.after(100, self.update_volume)

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
        self.current_volume = 0.0

        if self.recording_mode == "hold":
            detail = f"Solte {self.hotkey.upper()} p/ transcrever | {self.cancel_hotkey.upper()} cancela"
        else:
            detail = f"Aperte {self.hotkey.upper()} novam. p/ transcrever | {self.cancel_hotkey.upper()} cancela"

        self.set_status("Gravando...", detail, COLOR_RECORDING)
        self.update_record_button_ui()
        self.start_ui_loops()
        self.beep_start()

        def callback(indata, frames_count, time_info, status):
            if self.is_recording:
                self.frames.append(indata.copy())
                # Calcula o RMS (Root Mean Square) para o indicador de volume
                rms = float(np.sqrt(np.mean(indata**2)))
                self.current_volume = rms

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
            self.stop_ui_loops()
            self.update_record_button_ui()
            self.set_status("Erro", str(e), COLOR_ERROR)
            self.beep_error()

    def stop_and_process(self):
        if not self.is_recording:
            return

        self.is_recording = False
        self.stop_ui_loops()

        try:
            if self.stream is not None:
                self.stream.stop()
                self.stream.close()
                self.stream = None
        except Exception:
            pass

        if not self.frames:
            self.update_record_button_ui()
            self.set_status("Pronto", self.ready_text, COLOR_READY)
            return

        audio_data = np.concatenate(self.frames, axis=0)

        self.is_processing = True
        self.update_record_button_ui()
        self.set_status("Carregando sua voz...", "Transcrevendo e salvando...", COLOR_PROCESSING)
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
        self.stop_ui_loops()

        try:
            if self.stream is not None:
                self.stream.stop()
                self.stream.close()
                self.stream = None
        except Exception:
            pass
            
        self.frames = []
        self.update_record_button_ui()
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
            self.root.after(0, self.update_record_button_ui)

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
            
        self.unregister_hotkeys()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = DitadoWidget(root)
    root.mainloop()


if __name__ == "__main__":
    main()
