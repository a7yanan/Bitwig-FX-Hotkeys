"""Purple -> blue theme with dark / light variants (Qt style sheet)."""
from __future__ import annotations

from string import Template

from PySide6.QtGui import QColor, QPalette
from PySide6.QtCore import Qt

from . import palette

_state = {"mode": "dark", "scheme": "aurora", "c": palette.build("dark", "aurora")}


def colors() -> dict:
    return _state["c"]


def scheme() -> str:
    return _state["scheme"]


def is_dark() -> bool:
    return _state["mode"] == "dark"


def resolve(mode: str, app) -> str:
    if mode in ("dark", "light"):
        return mode
    try:                                   # Qt 6.5+
        return "dark" if app.styleHints().colorScheme() == Qt.ColorScheme.Dark else "light"
    except Exception:                      # noqa: BLE001
        return "dark"


QSS = Template(r"""
* { font-family: "Segoe UI Variable Text", "Segoe UI", sans-serif; font-size: 10pt; color: $text; }
QMainWindow, QDialog { background: $bg; }
QWidget#root { background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 $bg, stop:1 $bg2); }
QLabel { background: transparent; }
QLabel#muted { color: $muted; }
QLabel#section { color: $muted; font-size: 8pt; font-weight: 700; }
QLabel#h1 { font-size: 21pt; font-weight: 700; }
QLabel#h2 { font-size: 12pt; font-weight: 600; }
QLabel#err { color: $danger; }
QLabel#okmsg { color: $ok; }

QFrame#sidebar { background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 $side_a, stop:1 $side_b);
                 border-right: 1px solid $border; }
QFrame#card { background: $surface; border: 1px solid $border; border-radius: 14px; }
QFrame#pill { background: $surface2; border: 1px solid $border; border-radius: 12px; }
QFrame#hero { background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 $grad_a, stop:1 $grad_b);
              border-radius: 16px; }
QFrame#hero QLabel { background: transparent; color: $on_accent; }
QFrame#hero QLabel#sub { color: $on_soft; }
QFrame#iconbox { background: $box; border-radius: 14px; }

QScrollArea { background: transparent; border: none; }
QScrollArea > QWidget > QWidget { background: transparent; }

QPushButton { background: $surface2; border: 1px solid $border; border-radius: 10px; padding: 8px 16px; }
QPushButton:hover { background: $hover; }
QPushButton:pressed { background: $border; }
QPushButton:disabled { color: $muted; }
QPushButton#primary { border: none; color: $on_accent; font-weight: 600;
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 $grad_a, stop:1 $grad_b); }
QPushButton#primary:hover { background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 $grad_a_hi, stop:1 $grad_b_hi); }
QPushButton#primary:disabled { background: $border; color: $muted; }
QPushButton#danger { color: $danger; }
QPushButton#danger:hover { background: rgba(244,63,94,40); }
QPushButton#ghost { background: transparent; border: none; text-align: left; padding: 10px 12px; }
QPushButton#ghost:hover { background: $hover; }
QPushButton#ghost:checked { background: $sel; font-weight: 600; }
QPushButton#seg { padding: 8px 20px; }
QPushButton#seg:checked { border: none; color: $on_accent; font-weight: 600;
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 $grad_a, stop:1 $grad_b); }
QPushButton#hotkey { font-family: "Cascadia Mono", "Consolas", monospace; padding: 9px 14px;
                     border: 1px dashed $muted; text-align: center; }
QPushButton#hotkey[capturing="true"] { border: 1px solid $grad_a; background: $sel; }

QLineEdit, QPlainTextEdit, QSpinBox, QComboBox { background: $surface2; border: 1px solid $border;
    border-radius: 10px; padding: 7px 10px; selection-background-color: $grad_a; selection-color: $on_accent; }
QLineEdit:focus, QPlainTextEdit:focus, QSpinBox:focus, QComboBox:focus { border: 1px solid $grad_a; }
QPlainTextEdit#code { font-family: "Cascadia Mono", "Consolas", monospace; font-size: 9.5pt; }
QSpinBox::up-button, QSpinBox::down-button { width: 0px; border: none; }
QComboBox::drop-down { border: none; width: 26px; }
QComboBox QAbstractItemView { background: $surface; border: 1px solid $border; outline: 0;
    selection-background-color: $sel; selection-color: $text; padding: 4px; }

QCheckBox { spacing: 8px; background: transparent; }
QCheckBox::indicator, QTableView::indicator { width: 17px; height: 17px; border-radius: 5px;
    border: 1px solid $muted; background: $surface2; }
QCheckBox::indicator:checked, QTableView::indicator:checked { border: none;
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 $grad_a, stop:1 $grad_b); }

QTableWidget { background: transparent; border: none; gridline-color: transparent; outline: 0;
    alternate-background-color: $alt; selection-background-color: $sel; selection-color: $text; }
QTableWidget::item { padding: 6px 8px; border: none; }
QTableWidget::item:selected { background: $sel; color: $text; }
QHeaderView { background: transparent; }
QHeaderView::section { background: transparent; border: none; border-bottom: 1px solid $border;
    padding: 9px 8px; color: $muted; font-weight: 600; }
QTableCornerButton::section { background: transparent; border: none; }

QListWidget { background: transparent; border: none; outline: 0; }
QListWidget#profiles::item { padding: 11px 12px; border-radius: 10px; margin: 2px 0; }
QListWidget#profiles::item:hover { background: $hover; }
QListWidget#profiles::item:selected { color: $text;
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 $sel_a, stop:1 $sel_b); }
QListWidget#log::item { padding: 8px 10px; border-bottom: 1px solid $border; }

QTabWidget::pane { border: none; top: 6px; }
QTabBar { background: transparent; }
QTabBar::tab { background: transparent; color: $muted; padding: 9px 18px; margin-right: 6px;
    border-bottom: 2px solid transparent; font-weight: 600; }
QTabBar::tab:hover { color: $text; }
QTabBar::tab:selected { color: $text; border-bottom: 2px solid $grad_a; }

QScrollBar:vertical { background: transparent; width: 10px; margin: 2px; }
QScrollBar::handle:vertical { background: $border; border-radius: 4px; min-height: 30px; }
QScrollBar::handle:vertical:hover { background: $muted; }
QScrollBar:horizontal { background: transparent; height: 10px; margin: 2px; }
QScrollBar::handle:horizontal { background: $border; border-radius: 4px; min-width: 30px; }
QScrollBar::add-line, QScrollBar::sub-line { width: 0; height: 0; }
QScrollBar::add-page, QScrollBar::sub-page { background: transparent; }

QToolTip { background: $surface; color: $text; border: 1px solid $border; padding: 6px; border-radius: 6px; }
QMenu { background: $surface; border: 1px solid $border; border-radius: 10px; padding: 6px; }
QMenu::item { padding: 8px 24px; border-radius: 6px; }
QMenu::item:selected { background: $sel; }
QMenu::separator { height: 1px; background: $border; margin: 6px 8px; }
""")


def _palette(c: dict) -> QPalette:
    p = QPalette()
    R = QPalette.ColorRole
    for role, key in ((R.Window, "bg"), (R.Base, "surface2"), (R.AlternateBase, "surface"),
                      (R.Button, "surface2"), (R.ToolTipBase, "surface"), (R.Text, "text"),
                      (R.WindowText, "text"), (R.ButtonText, "text"), (R.ToolTipText, "text"),
                      (R.PlaceholderText, "muted"), (R.Highlight, "grad_a")):
        p.setColor(role, QColor(c[key]))
    p.setColor(R.HighlightedText, QColor(c["on_accent"]))
    return p


def apply(app, mode: str, scheme: str = "aurora") -> None:
    real = resolve(mode, app)
    c = palette.build(real, scheme)
    _state.update(mode=real, scheme=scheme, c=c)
    app.setPalette(_palette(c))
    app.setStyleSheet(QSS.safe_substitute(c))
    for w in app.allWidgets():
        w.update()
