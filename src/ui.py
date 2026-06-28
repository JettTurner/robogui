import os
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit,
    QFileDialog, QTextEdit,
    QCheckBox, QSpinBox,
    QFrame, QScrollArea
)

from core import RoboCore

if getattr(sys, "frozen", False):
    _base = sys._MEIPASS
else:
    _base = os.path.dirname(os.path.dirname(__file__))
_icon_path = os.path.join(_base, "icon", "robogui.ico")


# -----------------------------
# COLLAPSIBLE BOX
# -----------------------------
class CollapsibleBox(QWidget):
    def __init__(self, title="", expanded=False):
        super().__init__()

        self.toggle_btn = QPushButton()
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setChecked(expanded)

        self.content = QFrame()
        self.content_layout = QVBoxLayout()
        self.content.setLayout(self.content_layout)

        self.toggle_btn.clicked.connect(self.toggle)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.toggle_btn)
        layout.addWidget(self.content)

        self.setLayout(layout)

        self.set_title(title, expanded)
        self.content.setVisible(expanded)

    def set_title(self, title, expanded):
        arrow = "▼" if expanded else "▶"
        self.toggle_btn.setText(f"{arrow} {title}")

    def toggle(self):
        visible = self.toggle_btn.isChecked()
        self.content.setVisible(visible)

        text = self.toggle_btn.text().replace("▼", "▶").replace("▶", "▼")
        self.toggle_btn.setText(text)


# -----------------------------
# MAIN WINDOW
# -----------------------------
class RoboGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("RoboGUI - Robocopy Manager")
        self.setWindowIcon(QIcon(_icon_path))

        # 🔥 IMPORTANT: prevent insane vertical growth
        self.resize(900, 600)
        self.setMinimumHeight(500)
        self.setMaximumHeight(700)

        self.core = RoboCore()

        self._build_ui()

    # -----------------------------
    # UI
    # -----------------------------
    def _build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)

        main = QVBoxLayout()

        # -----------------------------
        # TOP: SOURCE / DEST
        # -----------------------------
        top = QHBoxLayout()

        self.src_input = QLineEdit()
        self.dst_input = QLineEdit()

        btn_src = QPushButton("Browse")
        btn_dst = QPushButton("Browse")

        btn_src.clicked.connect(self.pick_src)
        btn_dst.clicked.connect(self.pick_dst)

        top.addWidget(QLabel("Source"))
        top.addWidget(self.src_input)
        top.addWidget(btn_src)

        top.addWidget(QLabel("Destination"))
        top.addWidget(self.dst_input)
        top.addWidget(btn_dst)

        main.addLayout(top)

        # -----------------------------
        # CENTER: SCROLL AREA (FIX HEIGHT ISSUE)
        # -----------------------------
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout()

        # -----------------------------
        # BASIC (OPEN)
        # -----------------------------
        self.basic = CollapsibleBox("Basic Options", expanded=True)

        self.mirror = QCheckBox("Mirror (/MIR)")
        self.subdirs = QCheckBox("Include Subdirs (/E)")

        self.mt = QSpinBox()
        self.mt.setRange(1, 128)
        self.mt.setValue(16)

        self.basic.content_layout.addWidget(self.mirror)
        self.basic.content_layout.addWidget(self.subdirs)
        self.basic.content_layout.addWidget(QLabel("Threads (/MT)"))
        self.basic.content_layout.addWidget(self.mt)

        # -----------------------------
        # ADVANCED (CLOSED)
        # -----------------------------
        self.advanced = CollapsibleBox("Advanced Options", expanded=False)

        self.restartable = QCheckBox("/Z Restartable")
        self.unbuffered = QCheckBox("/J Unbuffered")
        self.tee = QCheckBox("/TEE Output")
        self.noprogress = QCheckBox("/NP No Progress")

        self.advanced.content_layout.addWidget(self.restartable)
        self.advanced.content_layout.addWidget(self.unbuffered)
        self.advanced.content_layout.addWidget(self.tee)
        self.advanced.content_layout.addWidget(self.noprogress)

        # -----------------------------
        # RAW (CLOSED)
        # -----------------------------
        self.raw = CollapsibleBox("Raw Arguments", expanded=False)

        self.raw_cmd = QLineEdit()
        self.raw_cmd.setPlaceholderText("Custom robocopy flags override")

        self.raw.content_layout.addWidget(self.raw_cmd)

        # ADD TO SCROLL
        scroll_layout.addWidget(self.basic)
        scroll_layout.addWidget(self.advanced)
        scroll_layout.addWidget(self.raw)

        scroll_layout.addStretch()

        scroll_content.setLayout(scroll_layout)
        scroll.setWidget(scroll_content)

        main.addWidget(scroll)

        # -----------------------------
        # ACTIONS (FIXED FOOTER)
        # -----------------------------
        actions = QHBoxLayout()

        self.start_btn = QPushButton("START")
        self.stop_btn = QPushButton("STOP")
        self.dry_btn = QPushButton("DRY RUN")

        self.start_btn.setStyleSheet("background-color: green; color: white;")
        self.stop_btn.setStyleSheet("background-color: red; color: white;")

        self.start_btn.clicked.connect(self.run)
        self.stop_btn.clicked.connect(self.stop)
        self.dry_btn.clicked.connect(self.dry_run)

        actions.addWidget(self.start_btn)
        actions.addWidget(self.stop_btn)
        actions.addWidget(self.dry_btn)

        main.addLayout(actions)

        # -----------------------------
        # LOG (FIXED HEIGHT)
        # -----------------------------
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumHeight(160)

        main.addWidget(self.log)

        root.setLayout(main)

    # -----------------------------
    # FILE PICKERS
    # -----------------------------
    def pick_src(self):
        path = QFileDialog.getExistingDirectory(self)
        if path:
            self.src_input.setText(path)

    def pick_dst(self):
        path = QFileDialog.getExistingDirectory(self)
        if path:
            self.dst_input.setText(path)

    # -----------------------------
    # EXECUTION
    # -----------------------------
    def run(self):
        self.execute(dry=False)

    def dry_run(self):
        self.execute(dry=True)

    def stop(self):
        self.core.stop()
        self.log.append("Stopped process\n")

    def execute(self, dry=False):
        cfg = {
            "src": self.src_input.text(),
            "dst": self.dst_input.text(),
            "mirror": self.mirror.isChecked(),
            "subdirs_empty": self.subdirs.isChecked(),
            "mt": self.mt.value(),
            "restartable": self.restartable.isChecked(),
            "unbuffered": self.unbuffered.isChecked(),
            "tee": self.tee.isChecked(),
            "noprogress": self.noprogress.isChecked(),
            "dry_run": dry
        }

        cmd = self.core.build_command(cfg)

        self.log.append("Running:\n" + " ".join(cmd) + "\n\n")

        def out(line):
            self.log.append(line.strip())

        code = self.core.run(cmd, out)

        self.log.append(f"\nFinished (code {code})\n")