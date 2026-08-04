import sys
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QAction
from PySide6.QtCore import Qt

from time_announcer.ui import MainWindow


def make_tray_icon() -> QIcon:
    """Draws a small amber dot icon at runtime, so we don't need an
    external image asset file."""
    size = 22
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setBrush(QColor("#E8A33D"))
    painter.setPen(Qt.NoPen)
    margin = 3
    painter.drawEllipse(margin, margin, size - margin * 2, size - margin * 2)
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