import sys
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QAction
from PySide6.QtCore import Qt

from time_announcer.ui import MainWindow


def make_tray_icon() -> QIcon:
    """Draws a clock-face icon at runtime for the menu bar."""
    from PySide6.QtCore import QPointF
    from PySide6.QtGui import QPen
    import math

    size = 32
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    center = size / 2
    radius = size / 2 - 3

    # Clock face outline
    pen = QPen(QColor("#E8A33D"))
    pen.setWidth(3)
    pen.setCapStyle(Qt.RoundCap)
    painter.setPen(pen)
    painter.setBrush(Qt.NoBrush)
    painter.drawEllipse(QPointF(center, center), radius, radius)

    # Hour hand (pointing to ~2 o'clock)
    hour_angle = math.radians(60 - 90)
    hour_len = radius * 0.5
    painter.drawLine(
        QPointF(center, center),
        QPointF(center + hour_len * math.cos(hour_angle),
                center + hour_len * math.sin(hour_angle)),
    )

    # Minute hand (pointing to 12)
    minute_angle = math.radians(-90)
    minute_len = radius * 0.8
    painter.drawLine(
        QPointF(center, center),
        QPointF(center + minute_len * math.cos(minute_angle),
                center + minute_len * math.sin(minute_angle)),
    )

    # Center dot
    painter.setBrush(QColor("#E8A33D"))
    painter.setPen(Qt.NoPen)
    painter.drawEllipse(QPointF(center, center), 2.5, 2.5)

    painter.end()
    return QIcon(pixmap)


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # closing the window shouldn't quit the app

    window = MainWindow()
    window.show()

    tray_icon = QSystemTrayIcon(make_tray_icon(), app)
    tray_icon.setToolTip("Time Announcer")

    menu = QMenu()

    show_action = QAction("Show Window", app)
    show_action.triggered.connect(window.show)
    show_action.triggered.connect(window.raise_)
    show_action.triggered.connect(window.activateWindow)
    menu.addAction(show_action)

    toggle_action = QAction("Enable", app)

    def toggle_running():
        if window.running:
            window._stop()
            toggle_action.setText("Enable")
        else:
            window._start()
            toggle_action.setText("Disable")

    toggle_action.triggered.connect(toggle_running)
    menu.addAction(toggle_action)

    speak_now_action = QAction("Speak Now", app)
    speak_now_action.triggered.connect(window._announce)
    menu.addAction(speak_now_action)

    menu.addSeparator()

    quit_action = QAction("Quit", app)
    quit_action.triggered.connect(app.quit)
    menu.addAction(quit_action)

    tray_icon.setContextMenu(menu)
    tray_icon.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()