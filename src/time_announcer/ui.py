from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QSpinBox, QHBoxLayout
)
from PySide6.QtCore import QTimer, Qt

from time_announcer.speaker import Speaker


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Time Announcer")
        self.setFixedSize(300, 200)

        self.speaker = Speaker()

        # --- Widgets ---
        self.time_label = QLabel(self._current_time_str())
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setStyleSheet("font-size: 28px; font-weight: bold;")

        self.status_label = QLabel("Stopped")
        self.status_label.setAlignment(Qt.AlignCenter)

        self.interval_spinbox = QSpinBox()
        self.interval_spinbox.setRange(1, 120)
        self.interval_spinbox.setValue(30)
        self.interval_spinbox.setSuffix(" min")

        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")
        self.stop_button.setEnabled(False)

        # --- Layout ---
        interval_row = QHBoxLayout()
        interval_row.addWidget(QLabel("Interval:"))
        interval_row.addWidget(self.interval_spinbox)

        button_row = QHBoxLayout()
        button_row.addWidget(self.start_button)
        button_row.addWidget(self.stop_button)

        layout = QVBoxLayout()
        layout.addWidget(self.time_label)
        layout.addWidget(self.status_label)
        layout.addLayout(interval_row)
        layout.addLayout(button_row)
        self.setLayout(layout)

        # --- Timer that updates the clock display every second ---
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self._update_clock_display)
        self.clock_timer.start(1000)

        # --- Timer that triggers the announcement ---
        self.announce_timer = QTimer(self)
        self.announce_timer.timeout.connect(self._announce)

        # --- Signals ---
        self.start_button.clicked.connect(self._start)
        self.stop_button.clicked.connect(self._stop)

    def _current_time_str(self) -> str:
        return datetime.now().strftime("%I:%M %p")

    def _update_clock_display(self) -> None:
        self.time_label.setText(self._current_time_str())

    def _start(self) -> None:
        minutes = self.interval_spinbox.value()
        self.announce_timer.start(minutes * 60 * 1000)  # ms
        self.status_label.setText("Running")
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.interval_spinbox.setEnabled(False)

    def _stop(self) -> None:
        self.announce_timer.stop()
        self.status_label.setText("Stopped")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.interval_spinbox.setEnabled(True)

    def _announce(self) -> None:
        current_time = self._current_time_str()
        self.speaker.say(f"It is now {current_time}")