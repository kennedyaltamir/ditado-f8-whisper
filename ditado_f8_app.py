import logging
import os
import platform
import queue
import time
import tkinter as tk
from enum import Enum, auto

import keyboard

from ditado_f8_widget import BASE_DIR, DitadoWidget
from logging_service import configure_logging, get_logger, log_event


class AppState(Enum):
    IDLE = auto()
    RECORDING = auto()
    PROCESSING = auto()
    CANCELLING = auto()
    ERROR = auto()
    SHUTTING_DOWN = auto()
    CLOSED = auto()


class AppEvent(Enum):
    HOTKEY_DOWN = auto()
    HOTKEY_UP = auto()
    BUTTON_START = auto()
    BUTTON_STOP = auto()
    CANCEL = auto()
    APPLICATION_CLOSE = auto()


class EventDrivenDitadoWidget(DitadoWidget):
    """Transitional controller that serializes user-input events on Tk's thread.

    The existing DitadoWidget remains the functional implementation for now.
    Global keyboard callbacks only publish events here; recording/UI methods are
    invoked by the dispatcher that runs from Tk's event loop.
    """

    EVENT_POLL_MS = 15

    def __init__(self, root):
        self.logger = get_logger()
        self._event_queue = queue.SimpleQueue()
        self.app_state = AppState.IDLE
        self._closing = False
        self._hotkey_latched = False
        self._event_job = None

        log_event(self.logger, "application_controller_init")
        super().__init__(root)

        log_event(
            self.logger,
            "config_loaded",
            hotkey=self.hotkey,
            cancel_hotkey=self.cancel_hotkey,
            recording_mode=self.recording_mode,
            auto_paste=bool(self.config.get("auto_paste", True)),
            save_audio=bool(self.config.get("save_audio", True)),
            save_txt=bool(self.config.get("save_txt", True)),
            always_on_top=bool(self.config.get("always_on_top", True)),
            save_dir=self.save_dir,
        )
        log_event(
            self.logger,
            "application_ready",
            state=self.app_state.name,
            device_index=self.device_index,
        )
        self._event_job = self.root.after(self.EVENT_POLL_MS, self._drain_events)

    def _set_state(self, new_state, reason):
        old_state = self.app_state
        if old_state is new_state:
            log_event(
                self.logger,
                "state_unchanged",
                level=logging.DEBUG,
                state=new_state.name,
                reason=reason,
            )
            return

        self.app_state = new_state
        log_event(
            self.logger,
            "state_transition",
            from_state=old_state.name,
            to_state=new_state.name,
            reason=reason,
        )

    def publish_event(self, event):
        if self._closing and event is not AppEvent.APPLICATION_CLOSE:
            log_event(
                self.logger,
                "event_ignored",
                level=logging.DEBUG,
                event_name=event.name,
                state=self.app_state.name,
                reason="closing",
            )
            return

        self._event_queue.put(event)
        log_event(
            self.logger,
            "event_published",
            event_name=event.name,
            state=self.app_state.name,
        )

    def register_hotkeys(self):
        self._hotkey_latched = False
        log_event(
            self.logger,
            "hotkey_registering",
            hotkey=getattr(self, "hotkey", None),
            cancel_hotkey=getattr(self, "cancel_hotkey", None),
        )
        try:
            super().register_hotkeys()
        except Exception:
            self.logger.exception(
                "hotkey_register_error",
                extra={"event": "hotkey_register_error", "fields": {}},
            )
            raise
        log_event(
            self.logger,
            "hotkey_registered",
            hotkey=self.hotkey,
            cancel_hotkey=self.cancel_hotkey,
        )

    def unregister_hotkeys(self):
        log_event(self.logger, "hotkey_unregistering")
        try:
            super().unregister_hotkeys()
        except Exception:
            self.logger.exception(
                "hotkey_unregister_error",
                extra={"event": "hotkey_unregister_error", "fields": {}},
            )
            return
        log_event(self.logger, "hotkey_unregistered")

    def on_key_event(self, event):
        """Keyboard hook boundary: no Tk or recording method is called here."""
        if self._closing:
            return

        try:
            cancel_pressed = keyboard.is_pressed(self.cancel_hotkey)
            hotkey_pressed = keyboard.is_pressed(self.hotkey)
        except Exception:
            self.logger.exception(
                "hotkey_read_error",
                extra={"event": "hotkey_read_error", "fields": {}},
            )
            return

        if cancel_pressed:
            self.publish_event(AppEvent.CANCEL)
            return

        if hotkey_pressed:
            if not self._hotkey_latched:
                self._hotkey_latched = True
                self.publish_event(AppEvent.HOTKEY_DOWN)
        else:
            if self._hotkey_latched:
                self.publish_event(AppEvent.HOTKEY_UP)
            self._hotkey_latched = False

    def toggle_recording_from_button(self):
        log_event(
            self.logger,
            "record_button_pressed",
            state=self.app_state.name,
        )
        if self.app_state is AppState.RECORDING:
            self.publish_event(AppEvent.BUTTON_STOP)
        else:
            self.publish_event(AppEvent.BUTTON_START)

    def cancel_recording(self):
        log_event(
            self.logger,
            "cancel_button_or_command",
            state=self.app_state.name,
        )
        self.publish_event(AppEvent.CANCEL)

    def on_close(self):
        log_event(
            self.logger,
            "application_close_requested",
            state=self.app_state.name,
        )
        self.publish_event(AppEvent.APPLICATION_CLOSE)

    def _drain_events(self):
        self._event_job = None

        while True:
            try:
                event = self._event_queue.get_nowait()
            except queue.Empty:
                break
            self._dispatch_event(event)

        if self.app_state is AppState.PROCESSING and not self.is_processing:
            self._set_state(AppState.IDLE, "legacy_processing_finished")

        if not self._closing and self.app_state is not AppState.CLOSED:
            self._event_job = self.root.after(self.EVENT_POLL_MS, self._drain_events)

    def _dispatch_event(self, event):
        log_event(
            self.logger,
            "event_dispatch",
            event_name=event.name,
            state=self.app_state.name,
        )

        if event is AppEvent.APPLICATION_CLOSE:
            if self.app_state not in (AppState.SHUTTING_DOWN, AppState.CLOSED):
                self._perform_close()
            else:
                log_event(
                    self.logger,
                    "event_ignored",
                    level=logging.DEBUG,
                    event_name=event.name,
                    state=self.app_state.name,
                    reason="already_closing",
                )
            return

        if self.app_state in (AppState.SHUTTING_DOWN, AppState.CLOSED):
            log_event(
                self.logger,
                "event_ignored",
                level=logging.DEBUG,
                event_name=event.name,
                state=self.app_state.name,
                reason="shutdown_state",
            )
            return

        if event is AppEvent.CANCEL:
            if self.app_state is AppState.RECORDING:
                self._set_state(AppState.CANCELLING, "cancel_event")
                log_event(self.logger, "recording_cancel_requested")
                DitadoWidget.cancel_recording(self)
                log_event(self.logger, "recording_cancelled")
                self._set_state(AppState.IDLE, "cancel_complete")
            else:
                log_event(
                    self.logger,
                    "event_ignored",
                    level=logging.DEBUG,
                    event_name=event.name,
                    state=self.app_state.name,
                    reason="not_recording",
                )
            return

        if event is AppEvent.BUTTON_START:
            if self.app_state is AppState.IDLE:
                self._start_recording_from_dispatcher("button")
            else:
                self._log_invalid_event(event)
            return

        if event is AppEvent.BUTTON_STOP:
            if self.app_state is AppState.RECORDING:
                self._stop_recording_from_dispatcher("button")
            else:
                self._log_invalid_event(event)
            return

        if event is AppEvent.HOTKEY_DOWN:
            if self.recording_mode == "toggle":
                if self.app_state is AppState.IDLE:
                    self._start_recording_from_dispatcher("hotkey_toggle")
                elif self.app_state is AppState.RECORDING:
                    self._stop_recording_from_dispatcher("hotkey_toggle")
                else:
                    self._log_invalid_event(event)
            elif self.app_state is AppState.IDLE:
                self._start_recording_from_dispatcher("hotkey_hold")
            else:
                self._log_invalid_event(event)
            return

        if event is AppEvent.HOTKEY_UP:
            if self.recording_mode == "hold" and self.app_state is AppState.RECORDING:
                self._stop_recording_from_dispatcher("hotkey_hold")
            elif self.recording_mode == "hold":
                self._log_invalid_event(event)
            return

    def _log_invalid_event(self, event):
        log_event(
            self.logger,
            "event_ignored",
            level=logging.DEBUG,
            event_name=event.name,
            state=self.app_state.name,
            reason="invalid_for_state",
        )

    def _start_recording_from_dispatcher(self, source):
        log_event(
            self.logger,
            "recording_start_requested",
            source=source,
            recording_mode=self.recording_mode,
            device_index=self.device_index,
        )
        DitadoWidget.start_recording(self)

        if self.is_recording:
            self._set_state(AppState.RECORDING, "recording_started")
            log_event(
                self.logger,
                "recording_started",
                source=source,
                recording_mode=self.recording_mode,
                sample_rate=self.config.get("sample_rate", 16000),
                channels=self.config.get("channels", 1),
                device_index=self.device_index,
            )
        else:
            self._set_state(AppState.IDLE, "recording_start_failed")
            log_event(
                self.logger,
                "recording_start_failed",
                level=logging.ERROR,
                source=source,
            )

    def _stop_recording_from_dispatcher(self, source):
        duration_seconds = max(0.0, time.time() - self.recording_start_time)
        frame_chunks = len(self.frames)
        log_event(
            self.logger,
            "recording_stop_requested",
            source=source,
            duration_seconds=round(duration_seconds, 3),
            frame_chunks=frame_chunks,
        )

        DitadoWidget.stop_and_process(self)

        if self.is_processing:
            log_event(
                self.logger,
                "recording_stopped",
                source=source,
                duration_seconds=round(duration_seconds, 3),
                frame_chunks=frame_chunks,
            )
            log_event(self.logger, "processing_started")
            self._set_state(AppState.PROCESSING, "processing_started")
        elif self.is_recording:
            self._set_state(AppState.RECORDING, "recording_stop_incomplete")
        else:
            log_event(
                self.logger,
                "recording_stopped_without_audio",
                source=source,
                duration_seconds=round(duration_seconds, 3),
            )
            self._set_state(AppState.IDLE, "recording_finished_without_processing")

    def find_input_device(self):
        mic_name = self.config.get("microphone_name_contains", "Iriun")
        log_event(
            self.logger,
            "microphone_detection_start",
            microphone_name_contains=mic_name,
        )
        try:
            device_index = DitadoWidget.find_input_device(self)
        except Exception:
            self.logger.exception(
                "microphone_detection_error",
                extra={
                    "event": "microphone_detection_error",
                    "fields": {"microphone_name_contains": mic_name},
                },
            )
            raise

        display_name = self.mic_var.get() if hasattr(self, "mic_var") else None
        log_event(
            self.logger,
            "microphone_detection_success",
            device_index=device_index,
            device_display=display_name,
        )
        return device_index

    def open_settings(self):
        log_event(self.logger, "settings_open_requested")
        return DitadoWidget.open_settings(self)

    def show_feedback(self, msg, color):
        log_event(
            self.logger,
            "settings_feedback",
            message=msg,
        )
        return DitadoWidget.show_feedback(self, msg, color)

    def save_settings(self, new_hotkey, mode_str, new_cancel, auto_paste, on_top):
        before = {
            "hotkey": self.hotkey,
            "cancel_hotkey": self.cancel_hotkey,
            "recording_mode": self.recording_mode,
            "auto_paste": bool(self.config.get("auto_paste", True)),
            "always_on_top": bool(self.config.get("always_on_top", True)),
        }
        log_event(
            self.logger,
            "settings_save_requested",
            new_hotkey=new_hotkey.strip().lower(),
            new_cancel_hotkey=new_cancel.strip().lower(),
            requested_mode=mode_str,
            auto_paste=bool(auto_paste),
            always_on_top=bool(on_top),
        )

        result = DitadoWidget.save_settings(
            self,
            new_hotkey,
            mode_str,
            new_cancel,
            auto_paste,
            on_top,
        )

        after = {
            "hotkey": self.hotkey,
            "cancel_hotkey": self.cancel_hotkey,
            "recording_mode": self.recording_mode,
            "auto_paste": bool(self.config.get("auto_paste", True)),
            "always_on_top": bool(self.config.get("always_on_top", True)),
        }
        log_event(
            self.logger,
            "settings_save_finished",
            changed=before != after,
            **after,
        )
        return result

    def set_status(self, status, detail="", color=None):
        log_event(
            self.logger,
            "ui_status_change",
            status=status,
            detail=detail,
        )
        if color is None:
            return DitadoWidget.set_status(self, status, detail)
        return DitadoWidget.set_status(self, status, detail, color)

    def set_last_text(self, text):
        log_event(
            self.logger,
            "transcript_available",
            text_length=len(text or ""),
            empty=not bool(text),
        )
        return DitadoWidget.set_last_text(self, text)

    def set_last_file(self, wav_path, txt_path):
        log_event(
            self.logger,
            "last_files_updated",
            wav_name=os.path.basename(wav_path) if wav_path else None,
            txt_name=os.path.basename(txt_path) if txt_path else None,
        )
        return DitadoWidget.set_last_file(self, wav_path, txt_path)

    def add_history_item(self, text, wav_path, txt_path):
        log_event(
            self.logger,
            "history_item_added",
            text_length=len(text or ""),
            wav_name=os.path.basename(wav_path) if wav_path else None,
            txt_name=os.path.basename(txt_path) if txt_path else None,
        )
        return DitadoWidget.add_history_item(self, text, wav_path, txt_path)

    def copy_history_item(self, item):
        log_event(
            self.logger,
            "output_copy",
            source="history",
            text_length=len(item.get("text", "")),
        )
        return DitadoWidget.copy_history_item(self, item)

    def open_history_txt(self, item):
        txt_path = item.get("txt_path", "")
        log_event(
            self.logger,
            "history_txt_open_requested",
            txt_name=os.path.basename(txt_path) if txt_path else None,
            exists=os.path.exists(txt_path) if txt_path else False,
        )
        return DitadoWidget.open_history_txt(self, item)

    def use_history_item(self, item):
        log_event(
            self.logger,
            "history_item_reused",
            text_length=len(item.get("text", "")),
        )
        return DitadoWidget.use_history_item(self, item)

    def clear_history(self):
        log_event(
            self.logger,
            "history_cleared",
            previous_count=len(self.history_items),
        )
        return DitadoWidget.clear_history(self)

    def open_save_folder(self):
        log_event(self.logger, "storage_folder_open_requested", save_dir=self.save_dir)
        return DitadoWidget.open_save_folder(self)

    def open_last_audio(self):
        log_event(
            self.logger,
            "audio_open_requested",
            wav_name=os.path.basename(self.last_wav_path) if self.last_wav_path else None,
        )
        return DitadoWidget.open_last_audio(self)

    def open_last_txt(self):
        log_event(
            self.logger,
            "txt_open_requested",
            txt_name=os.path.basename(self.last_txt_path) if self.last_txt_path else None,
        )
        return DitadoWidget.open_last_txt(self)

    def copy_last_text(self):
        log_event(
            self.logger,
            "output_copy",
            source="last_text",
            text_length=len(self.last_text or ""),
        )
        return DitadoWidget.copy_last_text(self)

    def save_wav(self, path, audio_data):
        log_event(
            self.logger,
            "wav_save_start",
            wav_name=os.path.basename(path),
            sample_count=int(getattr(audio_data, "shape", [0])[0]),
        )
        try:
            result = DitadoWidget.save_wav(self, path, audio_data)
        except Exception:
            self.logger.exception(
                "wav_save_error",
                extra={
                    "event": "wav_save_error",
                    "fields": {"wav_name": os.path.basename(path)},
                },
            )
            raise
        log_event(self.logger, "wav_save_success", wav_name=os.path.basename(path))
        return result

    def save_txt(self, path, text):
        log_event(
            self.logger,
            "txt_save_start",
            txt_name=os.path.basename(path),
            text_length=len(text or ""),
        )
        try:
            result = DitadoWidget.save_txt(self, path, text)
        except Exception:
            self.logger.exception(
                "txt_save_error",
                extra={
                    "event": "txt_save_error",
                    "fields": {"txt_name": os.path.basename(path)},
                },
            )
            raise
        log_event(self.logger, "txt_save_success", txt_name=os.path.basename(path))
        return result

    def transcribe_wav(self, path):
        started_at = time.monotonic()
        executable = self.config.get("whisper_exe")
        model = self.config.get("model_path")
        log_event(
            self.logger,
            "whisper_start",
            executable=os.path.basename(executable) if executable else None,
            model=os.path.basename(model) if model else None,
            language=self.config.get("language", "pt"),
            wav_name=os.path.basename(path),
        )

        try:
            text = DitadoWidget.transcribe_wav(self, path)
        except Exception:
            self.logger.exception(
                "whisper_error",
                extra={
                    "event": "whisper_error",
                    "fields": {
                        "duration_seconds": round(time.monotonic() - started_at, 3),
                        "wav_name": os.path.basename(path),
                    },
                },
            )
            raise

        duration = round(time.monotonic() - started_at, 3)
        if text:
            log_event(
                self.logger,
                "whisper_success",
                duration_seconds=duration,
                text_length=len(text),
            )
        else:
            log_event(
                self.logger,
                "whisper_empty",
                level=logging.WARNING,
                duration_seconds=duration,
            )
        return text

    def process_audio(self, audio_data):
        sample_count = int(getattr(audio_data, "shape", [0])[0])
        log_event(
            self.logger,
            "processing_thread_enter",
            sample_count=sample_count,
        )
        try:
            return DitadoWidget.process_audio(self, audio_data)
        finally:
            log_event(
                self.logger,
                "processing_thread_exit",
                sample_count=sample_count,
            )

    def _perform_close(self):
        self._set_state(AppState.SHUTTING_DOWN, "application_close")
        self._closing = True
        log_event(
            self.logger,
            "application_shutdown_start",
            is_recording=self.is_recording,
            is_processing=self.is_processing,
        )
        try:
            DitadoWidget.on_close(self)
        finally:
            self._set_state(AppState.CLOSED, "application_closed")
            log_event(self.logger, "application_shutdown")


def main():
    logger = configure_logging(BASE_DIR)
    log_event(
        logger,
        "application_start",
        pid=os.getpid(),
        python_version=platform.python_version(),
        platform=platform.platform(),
    )

    root = tk.Tk()
    try:
        EventDrivenDitadoWidget(root)
        root.mainloop()
    except Exception:
        logger.exception(
            "unexpected_exception",
            extra={"event": "unexpected_exception", "fields": {"scope": "main"}},
        )
        raise
    finally:
        log_event(logger, "application_mainloop_exit")


if __name__ == "__main__":
    main()
