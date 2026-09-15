import queue
import tkinter as tk
from enum import Enum, auto

import keyboard

from ditado_f8_widget import DitadoWidget


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
        self._event_queue = queue.SimpleQueue()
        self.app_state = AppState.IDLE
        self._closing = False
        self._hotkey_latched = False
        self._event_job = None

        super().__init__(root)

        self._event_job = self.root.after(self.EVENT_POLL_MS, self._drain_events)

    def publish_event(self, event):
        if self._closing and event is not AppEvent.APPLICATION_CLOSE:
            return
        self._event_queue.put(event)

    def register_hotkeys(self):
        self._hotkey_latched = False
        super().register_hotkeys()

    def on_key_event(self, event):
        """Keyboard hook boundary: no Tk or recording method is called here."""
        if self._closing:
            return

        try:
            cancel_pressed = keyboard.is_pressed(self.cancel_hotkey)
            hotkey_pressed = keyboard.is_pressed(self.hotkey)
        except Exception:
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
        if self.app_state is AppState.RECORDING:
            self.publish_event(AppEvent.BUTTON_STOP)
        else:
            self.publish_event(AppEvent.BUTTON_START)

    def cancel_recording(self):
        self.publish_event(AppEvent.CANCEL)

    def on_close(self):
        self.publish_event(AppEvent.APPLICATION_CLOSE)

    def _drain_events(self):
        self._event_job = None

        while True:
            try:
                event = self._event_queue.get_nowait()
            except queue.Empty:
                break
            self._dispatch_event(event)

        # Transitional synchronization while process_audio still belongs to the
        # legacy widget. A later milestone will publish structured transcription
        # completion events instead of mirroring the legacy boolean.
        if self.app_state is AppState.PROCESSING and not self.is_processing:
            self.app_state = AppState.IDLE

        if not self._closing and self.app_state is not AppState.CLOSED:
            self._event_job = self.root.after(self.EVENT_POLL_MS, self._drain_events)

    def _dispatch_event(self, event):
        if event is AppEvent.APPLICATION_CLOSE:
            if self.app_state not in (AppState.SHUTTING_DOWN, AppState.CLOSED):
                self._perform_close()
            return

        if self.app_state in (AppState.SHUTTING_DOWN, AppState.CLOSED):
            return

        if event is AppEvent.CANCEL:
            if self.app_state is AppState.RECORDING:
                self.app_state = AppState.CANCELLING
                DitadoWidget.cancel_recording(self)
                self.app_state = AppState.IDLE
            return

        if event is AppEvent.BUTTON_START:
            if self.app_state is AppState.IDLE:
                self._start_recording_from_dispatcher()
            return

        if event is AppEvent.BUTTON_STOP:
            if self.app_state is AppState.RECORDING:
                self._stop_recording_from_dispatcher()
            return

        if event is AppEvent.HOTKEY_DOWN:
            if self.recording_mode == "toggle":
                if self.app_state is AppState.IDLE:
                    self._start_recording_from_dispatcher()
                elif self.app_state is AppState.RECORDING:
                    self._stop_recording_from_dispatcher()
            elif self.app_state is AppState.IDLE:
                self._start_recording_from_dispatcher()
            return

        if event is AppEvent.HOTKEY_UP:
            if self.recording_mode == "hold" and self.app_state is AppState.RECORDING:
                self._stop_recording_from_dispatcher()
            return

    def _start_recording_from_dispatcher(self):
        DitadoWidget.start_recording(self)
        self.app_state = AppState.RECORDING if self.is_recording else AppState.IDLE

    def _stop_recording_from_dispatcher(self):
        DitadoWidget.stop_and_process(self)
        if self.is_processing:
            self.app_state = AppState.PROCESSING
        elif self.is_recording:
            self.app_state = AppState.RECORDING
        else:
            self.app_state = AppState.IDLE

    def _perform_close(self):
        self.app_state = AppState.SHUTTING_DOWN
        self._closing = True
        try:
            DitadoWidget.on_close(self)
        finally:
            self.app_state = AppState.CLOSED


def main():
    root = tk.Tk()
    EventDrivenDitadoWidget(root)
    root.mainloop()


if __name__ == "__main__":
    main()
