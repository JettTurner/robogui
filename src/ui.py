import sys, os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QGroupBox,
    QPushButton, QLabel, QLineEdit,
    QFileDialog, QTextEdit,
    QCheckBox, QSpinBox, QButtonGroup,
    QFrame, QScrollArea
)

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from core import RoboCore


def resource_path(relative):
    """Get path to bundled asset — works in dev and PyInstaller --onefile.

    In dev, __file__ is src/ui.py so relative should start with '..'.
    Frozen, sys._MEIPASS is the bundle root so relative should not have '..'.
    """
    import sys
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS
        # strip leading '..\\' or '../' prefix since we're already at root
        parts = relative.replace("/", "\\").split("\\")
        while parts and parts[0] in ("..", "."):
            parts.pop(0)
        relative = "\\".join(parts)
    else:
        base = os.path.dirname(__file__)
    return os.path.join(base, relative)

DARK_CSS = """
QMainWindow, QWidget {
    background-color: #1e1e1e;
    color: #d4d4d4;
}
QGroupBox {
    background-color: #252526;
    border: 1px solid #3c3c3c;
    border-radius: 6px;
    margin-top: 14px;
    padding: 18px 12px 12px 12px;
    font-weight: bold;
    color: #cccccc;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 8px;
    color: #569cd6;
}
QLineEdit {
    background-color: #3c3c3c;
    color: #d4d4d4;
    border: 1px solid #555555;
    border-radius: 4px;
    padding: 5px 8px;
    selection-background-color: #264f78;
}
QLineEdit:focus {
    border-color: #569cd6;
}
QSpinBox {
    background-color: #3c3c3c;
    color: #d4d4d4;
    border: 1px solid #555555;
    border-radius: 4px;
    padding: 4px 6px;
}
QSpinBox:focus {
    border-color: #569cd6;
}
QPushButton {
    background-color: #0e639c;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 6px 16px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #1177bb;
}
QPushButton:pressed {
    background-color: #094771;
}
QCheckBox {
    color: #d4d4d4;
    spacing: 6px;
}
QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #555555;
    border-radius: 3px;
    background-color: #3c3c3c;
}
QCheckBox::indicator:checked {
    background-color: #0e639c;
    border-color: #0e639c;
}
QTextEdit {
    background-color: #1e1e1e;
    color: #d4d4d4;
    border: 1px solid #3c3c3c;
    border-radius: 4px;
    padding: 6px;
    font-family: "Consolas","Courier New",monospace;
    font-size: 12px;
    selection-background-color: #264f78;
}
QScrollArea {
    border: none;
    background: transparent;
}
QScrollBar:vertical {
    background: #1e1e1e;
    width: 10px;
}
QScrollBar::handle:vertical {
    background: #424242;
    border-radius: 5px;
    min-height: 20px;
}
QScrollBar::handle:vertical:hover {
    background: #555555;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QLabel {
    background: transparent;
}
"""


class CollapsibleBox(QWidget):
    def __init__(self, title="", expanded=False):
        super().__init__()

        self.toggle_btn = QPushButton()
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setChecked(expanded)
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: #2d2d2d;
                color: #569cd6;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
                padding: 8px 12px;
                text-align: left;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #383838;
                border-color: #569cd6;
            }
        """)

        self.content = QFrame()
        self.content.setStyleSheet("QFrame { background: transparent; border: none; }")
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(4, 4, 4, 4)
        self.content.setLayout(self.content_layout)

        self.toggle_btn.clicked.connect(self.toggle)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
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
        title = self.toggle_btn.text()[1:].strip()
        arrow = "▼" if visible else "▶"
        self.toggle_btn.setText(f"{arrow} {title}")


class SegmentedButtons(QWidget):
    def __init__(self, labels, default_index=0, tooltips=None):
        super().__init__()
        layout = QHBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        self.group = QButtonGroup()
        self.group.setExclusive(True)

        n = len(labels)
        for i, label in enumerate(labels):
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setChecked(i == default_index)

            if tooltips and i < len(tooltips):
                btn.setToolTip(tooltips[i])

            if i == 0:
                radius = "4px 0 0 4px"
                right = "none"
            elif i == n - 1:
                radius = "0 4px 4px 0"
                right = "1px solid #555555"
            else:
                radius = "0"
                right = "none"

            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #3c3c3c; color: #d4d4d4;
                    border: 1px solid #555555; border-right: {right};
                    border-radius: {radius};
                    padding: 6px 14px; font-weight: bold; font-size: 12px;
                }}
                QPushButton:checked {{
                    background-color: #0e639c; color: white; border-color: #0e639c;
                }}
                QPushButton:hover {{ background-color: #4a4a4a; }}
                QPushButton:checked:hover {{ background-color: #1177bb; }}
            """)

            self.group.addButton(btn, i)
            layout.addWidget(btn)

        self.setLayout(layout)


class RoboGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("RoboGUI - Robocopy Manager")
        self.resize(950, 680)
        self.setStyleSheet(DARK_CSS)

        icon_path = resource_path("..\\icon\\robogui.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.core = RoboCore()

        self._build_ui()

    def _build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)

        main = QVBoxLayout()
        main.setSpacing(8)
        main.setContentsMargins(12, 12, 12, 12)

        # -----------------------------
        # PATHS GROUP
        # -----------------------------
        paths_group = QGroupBox("Paths")
        paths_layout = QHBoxLayout()
        paths_layout.setSpacing(8)

        self.src_input = QLineEdit()
        self.src_input.setToolTip("Source directory to copy from")
        self.dst_input = QLineEdit()
        self.dst_input.setToolTip("Destination directory to copy to")

        btn_src = QPushButton("Browse")
        btn_src.setToolTip("Browse for source directory")
        btn_dst = QPushButton("Browse")
        btn_dst.setToolTip("Browse for destination directory")
        btn_src.clicked.connect(self.pick_src)
        btn_dst.clicked.connect(self.pick_dst)

        arrow = QLabel("  →  ")
        arrow.setStyleSheet("font-size: 20px; font-weight: bold; color: #569cd6; padding: 0 4px;")

        paths_layout.addWidget(QLabel("Source:"))
        paths_layout.addWidget(self.src_input, 1)
        paths_layout.addWidget(btn_src)
        paths_layout.addWidget(arrow)
        paths_layout.addWidget(QLabel("Dest:"))
        paths_layout.addWidget(self.dst_input, 1)
        paths_layout.addWidget(btn_dst)

        paths_group.setLayout(paths_layout)
        main.addWidget(paths_group)

        # -----------------------------
        # SCROLL AREA
        # -----------------------------
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        scroll_layout = QVBoxLayout()
        scroll_layout.setSpacing(4)

        # -----------------------------
        # BASIC OPTIONS (EXPANDED)
        # -----------------------------
        self.basic = CollapsibleBox("Basic Options", expanded=True)

        self.mode_btns = SegmentedButtons(
            ["Copy", "Mirror", "Purge", "Move", "MoveAll"], default_index=0,
            tooltips=[
                "Standard copy — no special mode flags",
                "Mirror source to dest — deletes extra files at destination (/MIR)",
                "Delete destination files that no longer exist in source (/PURGE)",
                "Move files — deletes source originals after copy (/MOV)",
                "Move files and dirs — deletes source originals including dirs (/MOVE)",
            ]
        )

        row_mode = QHBoxLayout()
        row_mode.addWidget(QLabel("Mode:"))
        row_mode.addWidget(self.mode_btns)
        row_mode.addStretch()
        self.basic.content_layout.addLayout(row_mode)

        self.subdir_btns = SegmentedButtons(
            ["None", "/S Subdirs", "/E Subdirs+Empty"], default_index=2,
            tooltips=[
                "Only copy files in the root directory — no subdirectories",
                "Include subdirectories, but skip empty ones (/S)",
                "Include all subdirectories including empty ones (/E) — default",
            ]
        )

        row_subdir = QHBoxLayout()
        row_subdir.addWidget(QLabel("Subdirs:"))
        row_subdir.addWidget(self.subdir_btns)
        row_subdir.addStretch()
        self.basic.content_layout.addLayout(row_subdir)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Threads (/MT):"))
        self.mt = QSpinBox()
        self.mt.setRange(1, 128)
        self.mt.setValue(16)
        self.mt.setToolTip("Number of parallel threads (1-128). Higher value speeds up many small files.")
        row2.addWidget(self.mt)
        row2.addSpacing(20)

        row2.addWidget(QLabel("Retries (/R):"))
        self.retries = QSpinBox()
        self.retries.setRange(0, 99)
        self.retries.setValue(2)
        self.retries.setToolTip("Number of retries on failed copies (/R). 0 = no retry.")
        row2.addWidget(self.retries)
        row2.addSpacing(20)

        row2.addWidget(QLabel("Wait (/W):"))
        self.wait = QSpinBox()
        self.wait.setRange(0, 999)
        self.wait.setValue(1)
        self.wait.setToolTip("Wait time between retries in seconds (/W)")
        row2.addWidget(self.wait)
        row2.addStretch()

        self.basic.content_layout.addLayout(row2)

        # -----------------------------
        # ADVANCED OPTIONS (COLLAPSED)
        # -----------------------------
        self.advanced = CollapsibleBox("Advanced Options", expanded=False)

        adv_row1 = QHBoxLayout()
        self.restartable = QCheckBox("/Z Restartable")
        self.restartable.setToolTip("Copy in restartable mode — resume interrupted transfers for large files")
        self.unbuffered = QCheckBox("/J Unbuffered")
        self.unbuffered.setToolTip("Use unbuffered I/O — faster for large files, less CPU overhead")
        adv_row1.addWidget(self.restartable)
        adv_row1.addWidget(self.unbuffered)
        adv_row1.addStretch()

        adv_row2 = QHBoxLayout()
        self.tee = QCheckBox("/TEE Output")
        self.tee.setToolTip("Output progress to both console and log file")
        self.noprogress = QCheckBox("/NP No Progress")
        self.noprogress.setToolTip("Suppress progress percentage — keeps output cleaner")
        adv_row2.addWidget(self.tee)
        adv_row2.addWidget(self.noprogress)
        adv_row2.addStretch()

        self.advanced.content_layout.addLayout(adv_row1)
        self.advanced.content_layout.addLayout(adv_row2)

        # -----------------------------
        # RAW ARGUMENTS (COLLAPSED)
        # -----------------------------
        self.raw = CollapsibleBox("Raw Arguments", expanded=False)

        self.raw_cmd = QLineEdit()
        self.raw_cmd.setPlaceholderText("Custom robocopy flags override")
        self.raw_cmd.setToolTip("Extra robocopy flags — applied on top of GUI settings")
        self.raw.content_layout.addWidget(self.raw_cmd)

        self.basic.toggle_btn.setToolTip("Basic copy options — mode, subdirectories, threads, retries")
        self.advanced.toggle_btn.setToolTip("Advanced options — restartable, unbuffered, logging")
        self.raw.toggle_btn.setToolTip("Custom raw robocopy flags")

        scroll_layout.addWidget(self.basic)
        scroll_layout.addWidget(self.advanced)
        scroll_layout.addWidget(self.raw)
        scroll_layout.addStretch()

        scroll_content.setLayout(scroll_layout)
        scroll.setWidget(scroll_content)

        main.addWidget(scroll)

        # -----------------------------
        # ACTIONS (FOOTER)
        # -----------------------------
        actions = QHBoxLayout()

        self.start_btn = QPushButton("▶  START")
        self.start_btn.setToolTip("Begin the robocopy operation with current settings")
        self.stop_btn = QPushButton("■  STOP")
        self.stop_btn.setToolTip("Stop the currently running robocopy process")
        self.dry_btn = QPushButton("◉  DRY RUN")
        self.dry_btn.setToolTip("Simulate — show what would be copied without actually copying (/L)")

        self.start_btn.setObjectName("startBtn")
        self.stop_btn.setObjectName("stopBtn")
        self.dry_btn.setObjectName("dryBtn")

        self.start_btn.setStyleSheet(
            "QPushButton { background-color: #1b7a1b; padding: 8px 24px; font-size: 14px; }"
            "QPushButton:hover { background-color: #228b22; }"
            "QPushButton:pressed { background-color: #145214; }"
        )
        self.stop_btn.setStyleSheet(
            "QPushButton { background-color: #8b1a1a; padding: 8px 24px; font-size: 14px; }"
            "QPushButton:hover { background-color: #a32424; }"
            "QPushButton:pressed { background-color: #661313; }"
        )
        self.dry_btn.setStyleSheet(
            "QPushButton { background-color: #8b6914; padding: 8px 24px; font-size: 14px; }"
            "QPushButton:hover { background-color: #a37d18; }"
            "QPushButton:pressed { background-color: #664e0e; }"
        )

        self.start_btn.clicked.connect(self.run)
        self.stop_btn.clicked.connect(self.stop)
        self.dry_btn.clicked.connect(self.dry_run)

        actions.addStretch()
        actions.addWidget(self.start_btn)
        actions.addSpacing(8)
        actions.addWidget(self.stop_btn)
        actions.addSpacing(8)
        actions.addWidget(self.dry_btn)
        actions.addStretch()

        main.addLayout(actions)

        # -----------------------------
        # LOG
        # -----------------------------
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumHeight(180)
        self.log.setToolTip("Output log — robocopy command and results appear here")

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
        modes = ["copy", "mirror", "purge", "move", "moveall"]
        subdirs = ["none", "s", "e"]

        cfg = {
            "src": self.src_input.text(),
            "dst": self.dst_input.text(),
            "mode": modes[self.mode_btns.group.checkedId()],
            "subdirs": subdirs[self.subdir_btns.group.checkedId()],
            "mt": self.mt.value(),
            "retries": self.retries.value(),
            "wait": self.wait.value(),
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
