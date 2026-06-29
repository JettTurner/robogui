from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QPushButton, QLabel, QLineEdit, QFileDialog,
    QGridLayout, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal

from core import RoboCore


DEFAULT_CFG = {
    "src": "", "dst": "", "mode": "copy", "subdirs": "e",
    "mt": 16, "retries": 2, "wait": 1, "dry_run": False,
    "z": False, "b": False, "zb": False, "j": False, "efsraw": False,
    "copy_flags": "", "dcopy_flags": "", "sec": False, "copyall": False,
    "nocopy": False, "secfix": False, "timfix": False, "add_attr": "",
    "remove_attr": "", "create": False, "fat": False, "no256": False,
    "sj": False, "sl": False, "nodcopy": False, "nooffload": False,
    "compress": False, "noclone": False, "sparse": "",
    "lev": 0, "mon": 0, "mot": 0, "rh": "", "pf": False, "ipg": 0,
    "iomaxsize": "", "iorate": "", "threshold": "",
    "archive_a": False, "archive_m": False, "include_attr": "",
    "exclude_attr": "", "exclude_files": "", "exclude_dirs": "",
    "xc": False, "xn": False, "xo": False, "xx": False, "xl": False,
    "im": False, "is_same": False, "it": False,
    "max_size": 0, "min_size": 0, "max_age": 0, "min_age": 0,
    "max_lad": 0, "min_lad": 0, "xj": False, "fft": False,
    "dst_comp": False, "xjd": False, "xjf": False,
    "reg": False, "tbd": False, "lfsm": False, "lfsm_size": "",
    "list_only": False, "x_report": False, "v": False, "ts": False,
    "fp": False, "bytes": False, "ns": False, "nc": False, "nfl": False,
    "ndl": False, "eta": False, "njh": False, "njs": False,
    "unicode": False, "log_tee": False,
    "log_file": "", "log_append_file": "", "unilog_file": "",
    "unilog_append_file": "",
    "job_name": "", "save_name": "", "quit": False, "nosd": False,
    "nodd": False, "if_files": "",
}

PRESETS = [
    {
        "name": "Quick Backup",
        "desc": "Copy all files and folders including empty ones. Best for everyday backups.",
        "tags": "/E /COPY:DAT /MT:16",
        "cfg": {
            "mode": "copy", "subdirs": "e", "mt": 16,
            "retries": 2, "wait": 1,
        },
    },
    {
        "name": "Mirror Sync",
        "desc": "Exact 1:1 mirror — destination becomes identical to source. Deletes extra files.",
        "tags": "/MIR /MT:16",
        "cfg": {
            "mode": "mirror", "subdirs": "e", "mt": 16,
            "retries": 2, "wait": 1,
        },
    },
    {
        "name": "Full Backup + Security",
        "desc": "Preserves all file data, attributes, timestamps, ACLs, owner, and auditing info.",
        "tags": "/E /COPY:DATSOU /MT:8",
        "cfg": {
            "mode": "copy", "subdirs": "e", "mt": 8,
            "copy_flags": "DATSOU", "retries": 3, "wait": 5,
        },
    },
    {
        "name": "Large File Transfer",
        "desc": "Optimized for large files — unbuffered I/O and restartable mode.",
        "tags": "/E /J /Z /MT:4",
        "cfg": {
            "mode": "copy", "subdirs": "e", "mt": 4,
            "j": True, "z": True, "retries": 5, "wait": 15,
        },
    },
    {
        "name": "Network Friendly",
        "desc": "Throttled for network transfers with inter-packet gap and longer retries.",
        "tags": "/E /IPG:100 /MT:2",
        "cfg": {
            "mode": "copy", "subdirs": "e", "mt": 2,
            "ipg": 100, "retries": 10, "wait": 30,
        },
    },
    {
        "name": "Sync Missing Files",
        "desc": "Only copies new files from source to destination. Never deletes anything.",
        "tags": "/E /COPY:DAT",
        "cfg": {
            "mode": "copy", "subdirs": "e", "mt": 16,
            "retries": 2, "wait": 1,
        },
    },
    {
        "name": "Dry Run Preview",
        "desc": "Simulate the copy — see what would happen without actually copying anything.",
        "tags": "/L /E /X /V /TS /FP",
        "cfg": {
            "mode": "copy", "subdirs": "e",
            "list_only": True, "x_report": True, "v": True,
            "ts": True, "fp": True,
            "njh": True, "njs": True,
            "retries": 0, "wait": 1,
        },
    },
    {
        "name": "Age Filtered Backup",
        "desc": "Copy files modified between 1 and 365 days old. Great for archiving recent work.",
        "tags": "/E /MINAGE:1 /MAXAGE:365 /MT:16",
        "cfg": {
            "mode": "copy", "subdirs": "e", "mt": 16,
            "min_age": 1, "max_age": 365,
            "retries": 2, "wait": 1,
        },
    },
    {
        "name": "Move Files",
        "desc": "Copy then delete source files. All subdirectories included.",
        "tags": "/MOV /E /COPY:DAT",
        "cfg": {
            "mode": "move", "subdirs": "e",
            "retries": 2, "wait": 1,
        },
    },
]

CARD_STYLE = """
QFrame#presetCard {
    background-color: #252526;
    border: 1px solid #3c3c3c;
    border-radius: 8px;
    padding: 12px;
}
QFrame#presetCard:hover {
    border-color: #569cd6;
    background-color: #2a2d2e;
}
QLabel#cardName {
    font-size: 14px;
    font-weight: bold;
    color: #569cd6;
}
QLabel#cardDesc {
    font-size: 11px;
    color: #b0b0b0;
}
QLabel#cardTags {
    font-size: 11px;
    color: #6a9955;
    font-family: Consolas, monospace;
}
"""


class PresetsPage(QWidget):
    preset_selected = pyqtSignal(dict)
    next_clicked = pyqtSignal()

    def __init__(self, core):
        super().__init__()
        self.core = core
        self._build_ui()
        self.setStyleSheet(CARD_STYLE)

    def _build_ui(self):
        root = QVBoxLayout()
        root.setSpacing(8)
        root.setContentsMargins(12, 12, 12, 12)

        # ---- Paths ----
        paths_group = QGroupBox("Paths")
        paths_layout = QHBoxLayout()
        paths_layout.setSpacing(8)

        self.src_input = QLineEdit()
        self.src_input.setToolTip("Source directory to copy from")
        self.dst_input = QLineEdit()
        self.dst_input.setToolTip("Destination directory to copy to")

        btn_src = QPushButton("Browse")
        btn_src.setToolTip("Browse for source directory")
        btn_src.clicked.connect(self._pick_src)
        btn_dst = QPushButton("Browse")
        btn_dst.setToolTip("Browse for destination directory")
        btn_dst.clicked.connect(self._pick_dst)

        arrow = QLabel("  \u2192  ")
        arrow.setStyleSheet("font-size: 20px; font-weight: bold; color: #569cd6; padding: 0 4px;")

        paths_layout.addWidget(QLabel("Source:"))
        paths_layout.addWidget(self.src_input, 1)
        paths_layout.addWidget(btn_src)
        paths_layout.addWidget(arrow)
        paths_layout.addWidget(QLabel("Dest:"))
        paths_layout.addWidget(self.dst_input, 1)
        paths_layout.addWidget(btn_dst)

        paths_group.setLayout(paths_layout)
        root.addWidget(paths_group)

        # ---- Title row ----
        title_row = QHBoxLayout()
        title = QLabel("Choose a Preset")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #d4d4d4; padding: 8px 0;")
        title_row.addWidget(title)
        title_row.addStretch()
        self.adv_btn = QPushButton("Advanced Controls")
        self.adv_btn.setToolTip("Open the advanced options dialog")
        self.adv_btn.setStyleSheet(
            "QPushButton { background-color: #2d2d2d; color: #d4d4d4; border: 1px solid #555555; "
            "padding: 6px 16px; font-size: 12px; border-radius: 4px; }"
            "QPushButton:hover { background-color: #3c3c3c; }"
        )
        title_row.addWidget(self.adv_btn)
        root.addLayout(title_row)

        # ---- Preset Grid ----
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        grid_widget = QWidget()
        grid_widget.setStyleSheet("background: transparent;")
        grid = QGridLayout()
        grid.setSpacing(10)

        for i, preset in enumerate(PRESETS):
            card = self._build_card(preset)
            row, col = divmod(i, 2)
            grid.addWidget(card, row, col)

        grid_widget.setLayout(grid)
        scroll.setWidget(grid_widget)
        root.addWidget(scroll, 1)

        # ---- Command Preview ----
        preview_row = QHBoxLayout()
        preview_row.setSpacing(8)
        preview_label = QLabel("Command:")
        preview_label.setStyleSheet("font-weight: bold; color: #569cd6;")
        preview_row.addWidget(preview_label)

        self.cmd_preview = QLineEdit()
        self.cmd_preview.setReadOnly(True)
        self.cmd_preview.setPlaceholderText("Select a preset or adjust paths — command updates in real time")
        self.cmd_preview.setToolTip("Generated robocopy command line based on current selection")
        self.cmd_preview.setStyleSheet(
            "QLineEdit { background-color: #1e1e1e; color: #6a9955; border: 1px solid #3c3c3c; "
            "border-radius: 4px; padding: 5px 8px; font-family: Consolas, monospace; font-size: 12px; }"
        )
        preview_row.addWidget(self.cmd_preview, 1)

        root.addLayout(preview_row)

        # ---- Bottom Buttons ----
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.next_btn = QPushButton("Next \u2192")
        self.next_btn.setToolTip("Proceed to run the robocopy command")
        self.next_btn.setStyleSheet(
            "QPushButton { background-color: #0e639c; padding: 8px 24px; font-size: 13px; }"
            "QPushButton:hover { background-color: #1177bb; }"
        )
        self.next_btn.clicked.connect(self.next_clicked.emit)
        btn_row.addWidget(self.next_btn)
        root.addLayout(btn_row)

        self.setLayout(root)

    def _build_card(self, preset):
        card = QFrame()
        card.setObjectName("presetCard")
        layout = QVBoxLayout()
        layout.setSpacing(4)
        layout.setContentsMargins(12, 10, 12, 10)

        name = QLabel(preset["name"])
        name.setObjectName("cardName")
        layout.addWidget(name)

        desc = QLabel(preset["desc"])
        desc.setObjectName("cardDesc")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        tags = QLabel(preset["tags"])
        tags.setObjectName("cardTags")
        layout.addWidget(tags)

        use_btn = QPushButton("Use")
        use_btn.setToolTip(f"Load '{preset['name']}' settings into advanced mode")
        use_btn.setStyleSheet(
            "QPushButton { background-color: #1b7a1b; padding: 4px 20px; font-size: 12px; }"
            "QPushButton:hover { background-color: #228b22; }"
        )
        use_btn.clicked.connect(lambda checked, p=preset: self._use_preset(p))

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(use_btn)
        layout.addLayout(btn_row)

        card.setLayout(layout)
        return card

    def _use_preset(self, preset):
        merged = dict(DEFAULT_CFG)
        merged.update(preset["cfg"])
        merged["src"] = self.src_input.text()
        merged["dst"] = self.dst_input.text()
        self.preset_selected.emit(merged)

    def _pick_src(self):
        path = QFileDialog.getExistingDirectory(self)
        if path:
            self.src_input.setText(path)

    def _pick_dst(self):
        path = QFileDialog.getExistingDirectory(self)
        if path:
            self.dst_input.setText(path)

    def _update_preview(self):
        cfg = dict(DEFAULT_CFG)
        cfg["src"] = self.src_input.text()
        cfg["dst"] = self.dst_input.text()
        cmd = self.core.build_command(cfg)
        self.cmd_preview.setText(" ".join(cmd))
