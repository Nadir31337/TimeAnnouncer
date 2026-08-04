from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QSpinBox, QHBoxLayout
)
from PySide6.QtGui import QPainter, QPen, QColor
from PySide6.QtCore import Qt, QTimer, QRectF

from time_announcer.speaker import Speaker
from time_announcer.settings import Settings

STYLESHEET = """
QWidget {
    background-color: #14121A;
    color: #F2EFE9;
    font-family: -apple-system, "SF Pro Text";
}

#clockLabel {
    font-family: "SF Mono", Menlo, monospace;
    font-size: 30px;
    font-weight: 600;
    color: #F2EFE9;
}

#statusLabel {
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 2px;
    color: #8A8494;
}

QLabel#intervalCaption {
    font-size: 13px;
    color: #8A8494;
}

QSpinBox {
    background-color: #1E1B26;
    border: 1px solid #2C2836;
    border-radius: 8px;
    padding: 6px 10px;
    color: #F2EFE9;
    font-size: 14px;
    min-width: 70px;
}

QSpinBox::up-button, QSpinBox::down-button {
    width: 16px;
    border: none;
    background: transparent;
}

QPushButton {
    border: none;
    border-radius: 18px;
    padding: 10px 24px;
    font-size: 14px;
    font-weight: 600;
}

QPushButton#startButton {
    background-color: #E8A33D;
    color: #14121A;
}

QPushButton#startButton:hover {
    background-color: #F5B85C;
}

QPushButton#startButton:disabled {
    background-color: #2C2836;
    color: #6A6473;
}

QPushButton#stopButton {
    background-color: #1E1B26;
    color: #F2EFE9;
    border: 1px solid #2C2836;
}

QPushButton#stopButton:hover {
    background-color: #262230;
}

QPushButton#stopButton:disabled {
    background-color: #14121A;
    color: #4A4553;
    border: 1px solid #1E1B26;
}
"""


class TimeRing(QWidget):
    """A circular progress ring that fills as time elapses toward the
    next announcement, and flashes when it fires."""

    TRACK_COLOR = QColor("#2C2836")
    FILL_COLOR = QColor("#E8A33D")
    FLASH_COLOR = QColor("#F5C876")

    def __init__(self, parent=None):
        super().__init__(parent)
        self._progress = 0.0  # 0.0 to 1.0
        self._flash = False
        self.setMinimumSize(200, 200)

        self.inner_layout = QVBoxLayout(self)
        self.inner_layout.setAlignment(Qt.AlignCenter)
        self.inner_layout.setSpacing(6)

    def set_progress(self, value: float) -> None:
        self._progress = max(0.0, min(1.0, value))
        self.update()

    def flash(self) -> None:
        self._flash = True
        self.update()
        QTimer.singleShot(350, self._end_flash)

    def _end_flash(self) -> None:
        self._flash = False
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        side = min(self.width(), self.height())
        line_width = 8
        margin = line_width / 2 + 4
        rect = QRectF(
            (self.width() - side) / 2 + margin,
            (self.height() - side) / 2 + margin,
            side - margin * 2,
            side - margin * 2,
        )

        track_pen = QPen(self.TRACK_COLOR)
        track_pen.setWidth(line_width)
        track_pen.setCapStyle(Qt.RoundCap)
        painter.setPen(track_pen)
        painter.drawArc(rect, 0, 360 * 16)

        fill_color = self.FLASH_COLOR if self._flash else self.FILL_COLOR
        fill_pen = QPen(fill_color)
        fill_pen.setWidth(line_width)
        fill_pen.setCapStyle(Qt.RoundCap)
        painter.setPen(fill_pen)
        span = int(-self._progress * 360 * 16)  # negative = clockwise from top
        painter.drawArc(rect, 90 * 16, span)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Time Announcer")
        self.setFixedSize(340, 420)
        self.setStyleSheet(STYLESHEET)

        self.speaker = Speaker()
        self.settings = Settings()
        self.running = False
        self.interval_seconds = 30 * 60
        self.elapsed_seconds = 0

        # --- Ring + inner labels ---
        self.ring = TimeRing()
        self.time_label = QLabel(self._current_time_str())
        self.time_label.setObjectName("clockLabel")
        self.time_label.setAlignment(Qt.AlignCenter)
        self.status_label = QLabel("STOPPED")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.ring.inner_layout.addWidget(self.time_label)
        self.ring.inner_layout.addWidget(self.status_label)

        # --- Controls ---
        self.interval_caption = QLabel("Announce every")
        self.interval_caption.setObjectName("intervalCaption")

        self.interval_spinbox = QSpinBox()
        self.interval_spinbox.setRange(1, 120)
        self.interval_spinbox.setValue(self.settings.get("interval_minutes"))
        self.interval_spinbox.setSuffix(" min")

        self.start_button = QPushButton("Start")
        self.start_button.setObjectName("startButton")
        self.stop_button = QPushButton("Stop")
        self.stop_button.setObjectName("stopButton")
        self.stop_button.setEnabled(False)

        interval_row = QHBoxLayout()
        interval_row.setAlignment(Qt.AlignCenter)
        interval_row.setSpacing(10)
        interval_row.addWidget(self.interval_caption)
        interval_row.addWidget(self.interval_spinbox)

        button_row = QHBoxLayout()
        button_row.setSpacing(10)
        button_row.addWidget(self.start_button)
        button_row.addWidget(self.stop_button)

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 28, 30, 28)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.ring, alignment=Qt.AlignCenter)
        layout.addLayout(interval_row)
        layout.addLayout(button_row)
        self.setLayout(layout)

        # --- Single 1-second tick drives clock, ring, and announcements ---
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(1000)

        self.start_button.clicked.connect(self._start)
        self.stop_button.clicked.connect(self._stop)

        def closeEvent(self, event) -> None:
         """Instead of quitting the app, just hide the window — the app
         keeps running in the menu bar."""
         event.ignore()
         self.hide()

    def _current_time_str(self) -> str:
        return datetime.now().strftime("%I:%M %p")

    def _tick(self) -> None:
        self.time_label.setText(self._current_time_str())
        if self.running:
            self.elapsed_seconds += 1
            self.ring.set_progress(self.elapsed_seconds / self.interval_seconds)
            if self.elapsed_seconds >= self.interval_seconds:
                self._announce()
                self.elapsed_seconds = 0
                self.ring.set_progress(0)

    def _start(self) -> None:
        self.interval_seconds = self.interval_spinbox.value() * 60
        self.settings.set("interval_minutes", self.interval_spinbox.value())
        self.elapsed_seconds = 0
        self.running = True
        self.ring.set_progress(0)
        self.status_label.setText("RUNNING")
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.interval_spinbox.setEnabled(False)

    def _stop(self) -> None:
        self.running = False
        self.ring.set_progress(0)
        self.status_label.setText("STOPPED")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.interval_spinbox.setEnabled(True)

    def _announce(self) -> None:
        self.ring.flash()
        current_time = self._current_time_str()
        self.speaker.say(f"It is now {current_time}")