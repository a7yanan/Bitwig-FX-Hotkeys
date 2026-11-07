import os
import sys
import threading
import traceback

from PySide6.QtNetwork import QLocalServer, QLocalSocket
from PySide6.QtWidgets import QApplication

from fxhotkeys import config, theme
from fxhotkeys.engine import Engine
from fxhotkeys.ui import MainWindow

INSTANCE = "FXHotkeys.single.instance"


def _log_error(*args):
    try:
        with open(os.path.join(config.data_dir(), "error.log"), "a", encoding="utf-8") as f:
            f.write("".join(traceback.format_exception(*args)) + "\n")
    except OSError:
        pass


def main() -> int:
    sys.excepthook = lambda *a: _log_error(*a)
    threading.excepthook = lambda a: _log_error(a.exc_type, a.exc_value, a.exc_traceback)

    app = QApplication(sys.argv)
    app.setApplicationName("FX Hotkeys")
    app.setQuitOnLastWindowClosed(False)

    # single instance: a second launch just brings the first window up
    sock = QLocalSocket()
    sock.connectToServer(INSTANCE)
    if sock.waitForConnected(300):
        sock.write(b"show")
        sock.waitForBytesWritten(300)
        return 0
    QLocalServer.removeServer(INSTANCE)
    server = QLocalServer()
    server.listen(INSTANCE)

    app.setStyle("Fusion")
    cfg = config.load()
    theme.apply(app, cfg.settings.theme, cfg.settings.scheme)

    engine = Engine(cfg)
    engine.start()
    win = MainWindow(cfg, engine, server, INSTANCE)

    def on_conn():
        conn = server.nextPendingConnection()
        if conn:
            conn.close()
        win.show_window()
    server.newConnection.connect(on_conn)
    app.aboutToQuit.connect(engine.stop)

    hidden = "--tray" in sys.argv or cfg.settings.start_minimized
    if not (hidden and win.tray):
        win.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
