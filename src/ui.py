import sys, os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QGroupBox,
    QPushButton, QLabel, QLineEdit,
    QFileDialog, QTextEdit,
    QCheckBox, QSpinBox, QButtonGroup,
    QFrame, QScrollArea, QComboBox, QDialog,
    QStackedWidget
)

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon
from core import RoboCore
from presets import PresetsPage, DEFAULT_CFG


def resource_path(relative):
    import sys
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS
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
    min-height: 22px;
}
QSpinBox:focus {
    border-color: #569cd6;
}
QComboBox {
    background-color: #3c3c3c;
    color: #d4d4d4;
    border: 1px solid #555555;
    border-radius: 4px;
    padding: 4px 8px;
    min-height: 22px;
}
QComboBox:focus {
    border-color: #569cd6;
}
QComboBox::drop-down {
    border: none;
    width: 20px;
}
QComboBox::down-arrow {
    image: none;
    border: none;
}
QComboBox QAbstractItemView {
    background-color: #3c3c3c;
    color: #d4d4d4;
    selection-background-color: #264f78;
    border: 1px solid #555555;
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


class FullControlsDialog(QDialog):
    def __init__(self, core, parent=None):
        super().__init__(parent)
        self.core = core
        self.setWindowTitle("Full Controls")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        if parent:
            self.setStyleSheet(parent.styleSheet())
        self._build_ui()

    def _build_ui(self):
        main = QVBoxLayout()
        main.setSpacing(8)
        main.setContentsMargins(12, 12, 12, 12)

        # -----------------------------
        # SCROLL AREA
        # -----------------------------
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        scroll_layout = QVBoxLayout()
        scroll_layout.setSpacing(4)

        # ============================================================
        # MODE & PERFORMANCE (EXPANDED)
        # ============================================================
        self.basic = CollapsibleBox("Mode && Performance", expanded=False)
        self.basic.toggle_btn.setToolTip("Core copy mode, subdirectory handling, thread count, and retry settings")

        self.mode_btns = SegmentedButtons(
            ["Copy", "Mirror", "Purge", "Move", "MoveAll"], default_index=0,
            tooltips=[
                "Standard copy - no special mode flags",
                "Mirror source to dest - deletes extra files at destination (/MIR)",
                "Delete destination files that no longer exist in source (/PURGE)",
                "Move files - deletes source originals after copy (/MOV)",
                "Move files and dirs - deletes source originals including dirs (/MOVE)",
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
                "Only copy files in the root directory - no subdirectories",
                "Include subdirectories, but skip empty ones (/S)",
                "Include all subdirectories including empty ones (/E) - default",
            ]
        )

        row_subdir = QHBoxLayout()
        row_subdir.addWidget(QLabel("Subdirs:"))
        row_subdir.addWidget(self.subdir_btns)
        row_subdir.addStretch()
        self.basic.content_layout.addLayout(row_subdir)

        row_perf = QHBoxLayout()
        row_perf.addWidget(QLabel("Threads (/MT):"))
        self.mt = QSpinBox()
        self.mt.setRange(1, 128)
        self.mt.setValue(16)
        self.mt.setToolTip("Number of parallel threads (1-128). Higher value speeds up copying many small files. Incompatible with /IPG, /EFSRAW, /LFSM.")
        row_perf.addWidget(self.mt)
        row_perf.addSpacing(20)

        row_perf.addWidget(QLabel("Retries (/R):"))
        self.retries = QSpinBox()
        self.retries.setRange(0, 999999)
        self.retries.setValue(2)
        self.retries.setToolTip("Number of retries on failed copies (/R). Default is 1,000,000. Set 0 for no retry.")
        row_perf.addWidget(self.retries)
        row_perf.addSpacing(20)

        row_perf.addWidget(QLabel("Wait (/W):"))
        self.wait = QSpinBox()
        self.wait.setRange(0, 99999)
        self.wait.setValue(1)
        self.wait.setToolTip("Wait time between retries in seconds (/W). Default is 30.")
        row_perf.addWidget(self.wait)
        row_perf.addStretch()

        self.basic.content_layout.addLayout(row_perf)

        scroll_layout.addWidget(self.basic)

        # ============================================================
        # COPY OPTIONS (COLLAPSED)
        # ============================================================
        self.copy_opts = CollapsibleBox("Copy Options", expanded=False)
        self.copy_opts.toggle_btn.setToolTip("Copy behavior flags - restartable, backup, file properties, attributes, and more")

        c1 = QHBoxLayout()
        self.chk_z = QCheckBox("/Z Restartable")
        self.chk_z.setToolTip("Copy in restartable mode - resume interrupted transfers for large files")
        self.chk_b = QCheckBox("/B Backup")
        self.chk_b.setToolTip("Copy in backup mode - overrides file/folder permission settings (ACLs) that may block access")
        self.chk_zb = QCheckBox("/ZB Restart+Backup")
        self.chk_zb.setToolTip("Copy in restartable mode; if access denied, switches to backup mode")
        self.chk_j = QCheckBox("/J Unbuffered")
        self.chk_j.setToolTip("Use unbuffered I/O - recommended for large files, less CPU overhead")
        self.chk_efsraw = QCheckBox("/EFSRAW")
        self.chk_efsraw.setToolTip("Copy all encrypted files in EFS RAW mode. Incompatible with /MT.")
        c1.addWidget(self.chk_z)
        c1.addWidget(self.chk_b)
        c1.addWidget(self.chk_zb)
        c1.addWidget(self.chk_j)
        c1.addWidget(self.chk_efsraw)
        c1.addStretch()
        self.copy_opts.content_layout.addLayout(c1)

        c2 = QHBoxLayout()
        c2.addWidget(QLabel("/COPY:"))
        self.copy_flags = QLineEdit()
        self.copy_flags.setPlaceholderText("DAT (Data,Attr,Time)")
        self.copy_flags.setToolTip("File properties to copy: D=Data, A=Attributes, T=Timestamps, S=ACL, O=Owner, U=Auditing. Default: DAT")
        self.copy_flags.setMaximumWidth(200)
        c2.addWidget(self.copy_flags)
        c2.addSpacing(16)
        c2.addWidget(QLabel("/DCOPY:"))
        self.dcopy_flags = QLineEdit()
        self.dcopy_flags.setPlaceholderText("DA (Data,Attr)")
        self.dcopy_flags.setToolTip("Directory properties to copy: D=Data, A=Attributes, T=Timestamps, E=Extended Attr. Default: DA")
        self.dcopy_flags.setMaximumWidth(200)
        c2.addWidget(self.dcopy_flags)
        c2.addStretch()
        self.copy_opts.content_layout.addLayout(c2)

        c3 = QHBoxLayout()
        self.chk_sec = QCheckBox("/SEC")
        self.chk_sec.setToolTip("Copy files with security (equivalent to /COPY:DATS)")
        self.chk_copyall = QCheckBox("/COPYALL")
        self.chk_copyall.setToolTip("Copy all file information (equivalent to /COPY:DATSOU)")
        self.chk_nocopy = QCheckBox("/NOCOPY")
        self.chk_nocopy.setToolTip("Copy no file information (useful with /PURGE)")
        self.chk_secfix = QCheckBox("/SECFIX")
        self.chk_secfix.setToolTip("Fix file security on all files, even skipped ones")
        self.chk_timfix = QCheckBox("/TIMFIX")
        self.chk_timfix.setToolTip("Fix file times on all files, even skipped ones")
        c3.addWidget(self.chk_sec)
        c3.addWidget(self.chk_copyall)
        c3.addWidget(self.chk_nocopy)
        c3.addWidget(self.chk_secfix)
        c3.addWidget(self.chk_timfix)
        c3.addStretch()
        self.copy_opts.content_layout.addLayout(c3)

        c4 = QHBoxLayout()
        c4.addWidget(QLabel("/A+:"))
        self.add_attr = QLineEdit()
        self.add_attr.setPlaceholderText("RASHCNET")
        self.add_attr.setToolTip("Add attributes to copied files: R=Read, A=Archive, S=System, H=Hidden, C=Compressed, N=Not indexed, E=Encrypted, T=Temporary")
        self.add_attr.setMaximumWidth(160)
        c4.addWidget(self.add_attr)
        c4.addSpacing(16)
        c4.addWidget(QLabel("/A-:"))
        self.remove_attr = QLineEdit()
        self.remove_attr.setPlaceholderText("RASHCNETO")
        self.remove_attr.setToolTip("Remove attributes from copied files: R=Read, A=Archive, S=System, H=Hidden, C=Compressed, N=Not indexed, E=Encrypted, T=Temporary, O=Offline")
        self.remove_attr.setMaximumWidth(160)
        c4.addWidget(self.remove_attr)
        c4.addStretch()
        self.copy_opts.content_layout.addLayout(c4)

        c5 = QHBoxLayout()
        self.chk_create = QCheckBox("/CREATE")
        self.chk_create.setToolTip("Create directory tree and zero-length files only")
        self.chk_fat = QCheckBox("/FAT")
        self.chk_fat.setToolTip("Create destination files using 8.3 character-length FAT file names only")
        self.chk_no256 = QCheckBox("/256")
        self.chk_no256.setToolTip("Turn off support for paths longer than 256 characters")
        self.chk_sj = QCheckBox("/SJ")
        self.chk_sj.setToolTip("Copy junctions (soft-links) to destination path instead of link targets")
        self.chk_sl = QCheckBox("/SL")
        self.chk_sl.setToolTip("Don't follow symbolic links - create a copy of the link instead")
        c5.addWidget(self.chk_create)
        c5.addWidget(self.chk_fat)
        c5.addWidget(self.chk_no256)
        c5.addWidget(self.chk_sj)
        c5.addWidget(self.chk_sl)
        c5.addStretch()
        self.copy_opts.content_layout.addLayout(c5)

        c6 = QHBoxLayout()
        self.chk_nodcopy = QCheckBox("/NODCOPY")
        self.chk_nodcopy.setToolTip("Copy no directory info (default /DCOPY:DA still applies)")
        self.chk_nooffload = QCheckBox("/NOOFFLOAD")
        self.chk_nooffload.setToolTip("Copy files without using the Windows Copy Offload mechanism")
        self.chk_compress = QCheckBox("/COMPRESS")
        self.chk_compress.setToolTip("Request network compression during file transfer if applicable")
        self.chk_noclone = QCheckBox("/NOCLONE")
        self.chk_noclone.setToolTip("Don't attempt block cloning as an optimization")
        c6.addWidget(self.chk_nodcopy)
        c6.addWidget(self.chk_nooffload)
        c6.addWidget(self.chk_compress)
        c6.addWidget(self.chk_noclone)
        c6.addStretch()
        self.copy_opts.content_layout.addLayout(c6)

        c7 = QHBoxLayout()
        c7.addWidget(QLabel("/SPARSE:"))
        self.sparse_combo = QComboBox()
        self.sparse_combo.addItems(["Off (not set)", "Yes", "No"])
        self.sparse_combo.setToolTip("Enable or disable retaining sparse state of files during copy. Default is Yes if enabled.")
        self.sparse_combo.setMaximumWidth(140)
        c7.addWidget(self.sparse_combo)
        c7.addSpacing(16)
        c7.addWidget(QLabel("/LEV:"))
        self.lev = QSpinBox()
        self.lev.setRange(0, 999)
        self.lev.setValue(0)
        self.lev.setToolTip("Copy only top N levels of source directory tree. 0 = unlimited.")
        self.lev.setMaximumWidth(80)
        c7.addWidget(self.lev)
        c7.addSpacing(16)
        c7.addWidget(QLabel("/MON:"))
        self.mon = QSpinBox()
        self.mon.setRange(0, 999)
        self.mon.setValue(0)
        self.mon.setToolTip("Monitor source and run again when more than N changes detected. 0 = disabled.")
        self.mon.setMaximumWidth(80)
        c7.addWidget(self.mon)
        c7.addSpacing(16)
        c7.addWidget(QLabel("/MOT:"))
        self.mot = QSpinBox()
        self.mot.setRange(0, 999)
        self.mot.setValue(0)
        self.mot.setToolTip("Monitor source and run again every N minutes if changes detected. 0 = disabled.")
        self.mot.setMaximumWidth(80)
        c7.addWidget(self.mot)
        c7.addStretch()
        self.copy_opts.content_layout.addLayout(c7)

        c8 = QHBoxLayout()
        c8.addWidget(QLabel("/RH:"))
        self.rh = QLineEdit()
        self.rh.setPlaceholderText("hhmm-hhmm")
        self.rh.setToolTip("Specify run times when new copies can be started. Format: hhmm-hhmm (e.g. 0900-1700)")
        self.rh.setMaximumWidth(140)
        c8.addWidget(self.rh)
        c8.addSpacing(16)
        self.chk_pf = QCheckBox("/PF")
        self.chk_pf.setToolTip("Check run times on a per-file (not per-pass) basis")
        c8.addWidget(self.chk_pf)
        c8.addSpacing(16)
        c8.addWidget(QLabel("/IPG:"))
        self.ipg = QSpinBox()
        self.ipg.setRange(0, 99999)
        self.ipg.setValue(0)
        self.ipg.setToolTip("Inter-packet gap in milliseconds to free bandwidth on slow lines. 0 = disabled. Incompatible with /MT.")
        self.ipg.setMaximumWidth(80)
        c8.addWidget(self.ipg)
        c8.addStretch()
        self.copy_opts.content_layout.addLayout(c8)

        scroll_layout.addWidget(self.copy_opts)

        # ============================================================
        # FILE SELECTION (COLLAPSED)
        # ============================================================
        self.file_sel = CollapsibleBox("File Selection", expanded=False)
        self.file_sel.toggle_btn.setToolTip("File filtering options - attributes, exclusions, size/age filters")

        f1 = QHBoxLayout()
        self.chk_archive_a = QCheckBox("/A Archive only")
        self.chk_archive_a.setToolTip("Copy only files with the Archive attribute set")
        self.chk_archive_m = QCheckBox("/M Archive+Reset")
        self.chk_archive_m.setToolTip("Copy only files with Archive attribute set, then reset the Archive attribute")
        self.chk_xc = QCheckBox("/XC Excl.Chgd")
        self.chk_xc.setToolTip("Exclude existing files with same timestamp but different file sizes")
        self.chk_xn = QCheckBox("/XN Excl.Newer")
        self.chk_xn.setToolTip("Exclude source files newer than destination")
        self.chk_xo = QCheckBox("/XO Excl.Older")
        self.chk_xo.setToolTip("Exclude source files older than destination")
        f1.addWidget(self.chk_archive_a)
        f1.addWidget(self.chk_archive_m)
        f1.addWidget(self.chk_xc)
        f1.addWidget(self.chk_xn)
        f1.addWidget(self.chk_xo)
        f1.addStretch()
        self.file_sel.content_layout.addLayout(f1)

        f2 = QHBoxLayout()
        self.chk_xx = QCheckBox("/XX Excl.Extra")
        self.chk_xx.setToolTip("Exclude extra files and directories present in destination but not source")
        self.chk_xl = QCheckBox("/XL Excl.Lonely")
        self.chk_xl.setToolTip("Exclude lonely files and dirs present in source but not destination")
        self.chk_im = QCheckBox("/IM Incl.Modified")
        self.chk_im.setToolTip("Include modified files (differing change times)")
        self.chk_is = QCheckBox("/IS Incl.Same")
        self.chk_is.setToolTip("Include same files identical in name, size, times, and attributes")
        self.chk_it = QCheckBox("/IT Incl.Tweaked")
        self.chk_it.setToolTip("Include tweaked files with same name, size, times but different attributes")
        f2.addWidget(self.chk_xx)
        f2.addWidget(self.chk_xl)
        f2.addWidget(self.chk_im)
        f2.addWidget(self.chk_is)
        f2.addWidget(self.chk_it)
        f2.addStretch()
        self.file_sel.content_layout.addLayout(f2)

        f3 = QHBoxLayout()
        f3.addWidget(QLabel("/IA:"))
        self.include_attr = QLineEdit()
        self.include_attr.setPlaceholderText("RASHCNETO")
        self.include_attr.setToolTip("Include only files with any of the specified attributes set: R,A,S,H,C,N,E,T,O")
        self.include_attr.setMaximumWidth(140)
        f3.addWidget(self.include_attr)
        f3.addSpacing(16)
        f3.addWidget(QLabel("/XA:"))
        self.exclude_attr = QLineEdit()
        self.exclude_attr.setPlaceholderText("RASHCNETO")
        self.exclude_attr.setToolTip("Exclude files with any of the specified attributes set: R,A,S,H,C,N,E,T,O")
        self.exclude_attr.setMaximumWidth(140)
        f3.addWidget(self.exclude_attr)
        f3.addStretch()
        self.file_sel.content_layout.addLayout(f3)

        f4 = QHBoxLayout()
        f4.addWidget(QLabel("/XF:"))
        self.exclude_files = QLineEdit()
        self.exclude_files.setPlaceholderText("file1.txt *.bak")
        self.exclude_files.setToolTip("Exclude files matching the specified names or paths. Wildcards (* and ?) supported.")
        f4.addWidget(self.exclude_files, 1)
        f4.addSpacing(16)
        f4.addWidget(QLabel("/XD:"))
        self.exclude_dirs = QLineEdit()
        self.exclude_dirs.setPlaceholderText("dir1 temp*")
        self.exclude_dirs.setToolTip("Exclude directories matching the specified names and paths. Wildcards supported.")
        f4.addWidget(self.exclude_dirs, 1)
        self.file_sel.content_layout.addLayout(f4)

        f5 = QHBoxLayout()
        f5.addWidget(QLabel("/MAX:"))
        self.max_size = QSpinBox()
        self.max_size.setRange(0, 999999999)
        self.max_size.setValue(0)
        self.max_size.setToolTip("Maximum file size in bytes - exclude files larger than this. 0 = unlimited.")
        self.max_size.setMaximumWidth(120)
        f5.addWidget(self.max_size)
        f5.addSpacing(16)
        f5.addWidget(QLabel("/MIN:"))
        self.min_size = QSpinBox()
        self.min_size.setRange(0, 999999999)
        self.min_size.setValue(0)
        self.min_size.setToolTip("Minimum file size in bytes - exclude files smaller than this. 0 = unlimited.")
        self.min_size.setMaximumWidth(120)
        f5.addWidget(self.min_size)
        f5.addSpacing(16)
        f5.addWidget(QLabel("/MAXAGE:"))
        self.max_age = QSpinBox()
        self.max_age.setRange(0, 99999)
        self.max_age.setValue(0)
        self.max_age.setToolTip("Maximum file age in days - exclude files older than N days. 0 = no limit.")
        self.max_age.setMaximumWidth(80)
        f5.addWidget(self.max_age)
        f5.addSpacing(16)
        f5.addWidget(QLabel("/MINAGE:"))
        self.min_age = QSpinBox()
        self.min_age.setRange(0, 99999)
        self.min_age.setValue(0)
        self.min_age.setToolTip("Minimum file age in days - exclude files newer than N days. 0 = no limit.")
        self.min_age.setMaximumWidth(80)
        f5.addWidget(self.min_age)
        f5.addStretch()
        self.file_sel.content_layout.addLayout(f5)

        f6 = QHBoxLayout()
        f6.addWidget(QLabel("/MAXLAD:"))
        self.max_lad = QSpinBox()
        self.max_lad.setRange(0, 9999999)
        self.max_lad.setValue(0)
        self.max_lad.setToolTip("Maximum last access date - exclude files unused since N. If N<1900, N=days. Otherwise YYYYMMDD.")
        self.max_lad.setMaximumWidth(100)
        f6.addWidget(self.max_lad)
        f6.addSpacing(16)
        f6.addWidget(QLabel("/MINLAD:"))
        self.min_lad = QSpinBox()
        self.min_lad.setRange(0, 9999999)
        self.min_lad.setValue(0)
        self.min_lad.setToolTip("Minimum last access date - exclude files used since N. If N<1900, N=days. Otherwise YYYYMMDD.")
        self.min_lad.setMaximumWidth(100)
        f6.addWidget(self.min_lad)
        f6.addSpacing(16)
        self.chk_xj = QCheckBox("/XJ Junctions")
        self.chk_xj.setToolTip("Exclude junction points (normally included by default)")
        f6.addWidget(self.chk_xj)
        self.chk_xjd = QCheckBox("/XJD DirJunc")
        self.chk_xjd.setToolTip("Exclude junction points for directories")
        f6.addWidget(self.chk_xjd)
        self.chk_xjf = QCheckBox("/XJF FileJunc")
        self.chk_xjf.setToolTip("Exclude junction points for files")
        f6.addWidget(self.chk_xjf)
        f6.addStretch()
        self.file_sel.content_layout.addLayout(f6)

        f7 = QHBoxLayout()
        self.chk_fft = QCheckBox("/FFT FAT Times")
        self.chk_fft.setToolTip("Assume FAT file times (two-second precision) for comparison")
        self.chk_dst = QCheckBox("/DST DST Comp")
        self.chk_dst.setToolTip("Compensate for one-hour DST time differences")
        f7.addWidget(self.chk_fft)
        f7.addWidget(self.chk_dst)
        f7.addStretch()
        self.file_sel.content_layout.addLayout(f7)

        scroll_layout.addWidget(self.file_sel)

        # ============================================================
        # FILE THROTTLING (COLLAPSED)
        # ============================================================
        self.throttle = CollapsibleBox("File Throttling", expanded=False)
        self.throttle.toggle_btn.setToolTip("I/O bandwidth throttling options for limiting system load")

        t1 = QHBoxLayout()
        t1.addWidget(QLabel("/IOMAXSIZE:"))
        self.iomaxsize = QLineEdit()
        self.iomaxsize.setPlaceholderText("e.g. 64k, 1m, 2g")
        self.iomaxsize.setToolTip("Requested max I/O size per read/write cycle. Suffix: k=KB, m=MB, g=GB.")
        self.iomaxsize.setMaximumWidth(140)
        t1.addWidget(self.iomaxsize)
        t1.addSpacing(16)
        t1.addWidget(QLabel("/IORATE:"))
        self.iorate = QLineEdit()
        self.iorate.setPlaceholderText("e.g. 1m, 512k")
        self.iorate.setToolTip("Requested I/O rate in bytes per second. Suffix: k=KB/s, m=MB/s, g=GB/s.")
        self.iorate.setMaximumWidth(140)
        t1.addWidget(self.iorate)
        t1.addSpacing(16)
        t1.addWidget(QLabel("/THRESHOLD:"))
        self.threshold = QLineEdit()
        self.threshold.setPlaceholderText("e.g. 256k, 10m")
        self.threshold.setToolTip("File size threshold for throttling. Files below this size are not throttled. Suffix: k, m, g.")
        self.threshold.setMaximumWidth(140)
        t1.addWidget(self.threshold)
        t1.addStretch()
        self.throttle.content_layout.addLayout(t1)

        scroll_layout.addWidget(self.throttle)

        # ============================================================
        # RETRY OPTIONS (COLLAPSED)
        # ============================================================
        self.retry_opts = CollapsibleBox("Retry Options", expanded=False)
        self.retry_opts.toggle_btn.setToolTip("Additional retry settings - registry save, share wait, low free space mode")

        r1 = QHBoxLayout()
        self.chk_reg = QCheckBox("/REG Save defaults")
        self.chk_reg.setToolTip("Save /R and /W values as default settings in the registry")
        self.chk_tbd = QCheckBox("/TBD Wait shares")
        self.chk_tbd.setToolTip("Wait for share names to be defined (retry error 67)")
        r1.addWidget(self.chk_reg)
        r1.addWidget(self.chk_tbd)
        r1.addStretch()
        self.retry_opts.content_layout.addLayout(r1)

        r2 = QHBoxLayout()
        self.chk_lfsm = QCheckBox("/LFSM Low free space mode")
        self.chk_lfsm.setToolTip("Pause copy when destination volume free space drops below floor value. Incompatible with /MT and /EFSRAW.")
        r2.addWidget(self.chk_lfsm)
        r2.addSpacing(8)
        r2.addWidget(QLabel("Floor:"))
        self.lfsm_size = QLineEdit()
        self.lfsm_size.setPlaceholderText("e.g. 500m, 10g")
        self.lfsm_size.setToolTip("Floor size for low free space mode. Suffix: k=KB, m=MB, g=GB. Default is 10% of volume.")
        self.lfsm_size.setMaximumWidth(130)
        r2.addWidget(self.lfsm_size)
        r2.addStretch()
        self.retry_opts.content_layout.addLayout(r2)

        scroll_layout.addWidget(self.retry_opts)

        # ============================================================
        # LOGGING OPTIONS (COLLAPSED)
        # ============================================================
        self.log_opts = CollapsibleBox("Logging Options", expanded=False)
        self.log_opts.toggle_btn.setToolTip("Output verbosity, log file paths, and display controls")

        l1 = QHBoxLayout()
        self.chk_list = QCheckBox("/L List only")
        self.chk_list.setToolTip("List files only - do not copy, delete, or timestamp (like a dry run)")
        self.chk_xreport = QCheckBox("/X Extra files")
        self.chk_xreport.setToolTip("Report all extra files, not just selected ones")
        self.chk_v = QCheckBox("/V Verbose")
        self.chk_v.setToolTip("Produce verbose output and show all skipped files")
        self.chk_ts = QCheckBox("/S Timestamps")
        self.chk_ts.setToolTip("Include source file timestamps in output")
        self.chk_fp = QCheckBox("/FP Full paths")
        self.chk_fp.setToolTip("Include full path names of files in the output")
        self.chk_bytes = QCheckBox("/BYTES")
        self.chk_bytes.setToolTip("Print sizes as bytes")
        l1.addWidget(self.chk_list)
        l1.addWidget(self.chk_xreport)
        l1.addWidget(self.chk_v)
        l1.addWidget(self.chk_ts)
        l1.addWidget(self.chk_fp)
        l1.addWidget(self.chk_bytes)
        l1.addStretch()
        self.log_opts.content_layout.addLayout(l1)

        l2 = QHBoxLayout()
        self.chk_ns = QCheckBox("/NS No sizes")
        self.chk_ns.setToolTip("Don't log file sizes")
        self.chk_nc = QCheckBox("/NC No classes")
        self.chk_nc.setToolTip("Don't log file classes")
        self.chk_nfl = QCheckBox("/NFL No filenames")
        self.chk_nfl.setToolTip("Don't log file names")
        self.chk_ndl = QCheckBox("/NDL No dir names")
        self.chk_ndl.setToolTip("Don't log directory names")
        self.chk_eta = QCheckBox("/ETA Est.time")
        self.chk_eta.setToolTip("Show estimated time of arrival for copied files")
        self.chk_njh = QCheckBox("/NJH No header")
        self.chk_njh.setToolTip("Suppress job header in log output")
        self.chk_njs = QCheckBox("/NJS No summary")
        self.chk_njs.setToolTip("Suppress job summary in log output")
        l2.addWidget(self.chk_ns)
        l2.addWidget(self.chk_nc)
        l2.addWidget(self.chk_nfl)
        l2.addWidget(self.chk_ndl)
        l2.addWidget(self.chk_eta)
        l2.addWidget(self.chk_njh)
        l2.addWidget(self.chk_njs)
        l2.addStretch()
        self.log_opts.content_layout.addLayout(l2)

        l3 = QHBoxLayout()
        self.chk_unicode = QCheckBox("/UNICODE")
        self.chk_unicode.setToolTip("Display status output as Unicode text")
        self.chk_log_tee = QCheckBox("/TEE Console+Log")
        self.chk_log_tee.setToolTip("Write status output to both console window and log file")
        l3.addWidget(self.chk_unicode)
        l3.addWidget(self.chk_log_tee)
        l3.addStretch()
        self.log_opts.content_layout.addLayout(l3)

        l4 = QHBoxLayout()
        l4.addWidget(QLabel("/LOG:"))
        self.log_file = QLineEdit()
        self.log_file.setPlaceholderText("Path to log file (overwrites)")
        self.log_file.setToolTip("Write status output to log file (overwrites existing)")
        l4.addWidget(self.log_file, 1)
        self.log_browse = QPushButton("Browse")
        self.log_browse.setToolTip("Browse for log file")
        self.log_browse.clicked.connect(lambda: self.pick_file(self.log_file))
        l4.addWidget(self.log_browse)
        l4.addSpacing(8)
        l4.addWidget(QLabel("/LOG+:"))
        self.log_append_file = QLineEdit()
        self.log_append_file.setPlaceholderText("Path to log file (appends)")
        self.log_append_file.setToolTip("Write status output to log file (appends to existing)")
        l4.addWidget(self.log_append_file, 1)
        self.log_append_browse = QPushButton("Browse")
        self.log_append_browse.setToolTip("Browse for log file")
        self.log_append_browse.clicked.connect(lambda: self.pick_file(self.log_append_file))
        l4.addWidget(self.log_append_browse)
        self.log_opts.content_layout.addLayout(l4)

        l5 = QHBoxLayout()
        l5.addWidget(QLabel("/UNILOG:"))
        self.unilog_file = QLineEdit()
        self.unilog_file.setPlaceholderText("Path to Unicode log (overwrites)")
        self.unilog_file.setToolTip("Write status output to Unicode log file (overwrites existing)")
        l5.addWidget(self.unilog_file, 1)
        self.unilog_browse = QPushButton("Browse")
        self.unilog_browse.setToolTip("Browse for Unicode log file")
        self.unilog_browse.clicked.connect(lambda: self.pick_file(self.unilog_file))
        l5.addWidget(self.unilog_browse)
        l5.addSpacing(8)
        l5.addWidget(QLabel("/UNILOG+:"))
        self.unilog_append_file = QLineEdit()
        self.unilog_append_file.setPlaceholderText("Path to Unicode log (appends)")
        self.unilog_append_file.setToolTip("Write status output to Unicode log file (appends to existing)")
        l5.addWidget(self.unilog_append_file, 1)
        self.unilog_append_browse = QPushButton("Browse")
        self.unilog_append_browse.setToolTip("Browse for Unicode log file")
        self.unilog_append_browse.clicked.connect(lambda: self.pick_file(self.unilog_append_file))
        l5.addWidget(self.unilog_append_browse)
        self.log_opts.content_layout.addLayout(l5)

        scroll_layout.addWidget(self.log_opts)

        # ============================================================
        # JOB OPTIONS (COLLAPSED)
        # ============================================================
        self.job_opts = CollapsibleBox("Job Options", expanded=False)
        self.job_opts.toggle_btn.setToolTip("Job file management - save/load parameter sets, job control flags")

        j1 = QHBoxLayout()
        j1.addWidget(QLabel("/JOB:"))
        self.job_name = QLineEdit()
        self.job_name.setPlaceholderText("Job name to load")
        self.job_name.setToolTip("Load parameters from a named job file. Run /SAVE first to create the job file.")
        j1.addWidget(self.job_name, 1)
        j1.addSpacing(16)
        j1.addWidget(QLabel("/SAVE:"))
        self.save_name = QLineEdit()
        self.save_name.setPlaceholderText("Job name to save")
        self.save_name.setToolTip("Save current parameters to a named job file")
        j1.addWidget(self.save_name, 1)
        self.job_opts.content_layout.addLayout(j1)

        j2 = QHBoxLayout()
        self.chk_quit = QCheckBox("/QUIT")
        self.chk_quit.setToolTip("Quit after processing command line (to view parameters)")
        self.chk_nosd = QCheckBox("/NOSD No source")
        self.chk_nosd.setToolTip("Indicate that no source directory is specified")
        self.chk_nodd = QCheckBox("/NODD No dest")
        self.chk_nodd.setToolTip("Indicate that no destination directory is specified")
        j2.addWidget(self.chk_quit)
        j2.addWidget(self.chk_nosd)
        j2.addWidget(self.chk_nodd)
        j2.addStretch()
        self.job_opts.content_layout.addLayout(j2)

        j3 = QHBoxLayout()
        j3.addWidget(QLabel("/IF:"))
        self.if_files = QLineEdit()
        self.if_files.setPlaceholderText("Files to include")
        self.if_files.setToolTip("Include only specified files")
        j3.addWidget(self.if_files, 1)
        self.job_opts.content_layout.addLayout(j3)

        scroll_layout.addWidget(self.job_opts)

        # ============================================================
        # RAW ARGUMENTS (COLLAPSED)
        # ============================================================
        self.raw = CollapsibleBox("Raw Arguments", expanded=False)
        self.raw.toggle_btn.setToolTip("Custom robocopy flags - appended on top of GUI settings")

        self.raw_cmd = QLineEdit()
        self.raw_cmd.setPlaceholderText("Extra robocopy flags — applied on top of GUI settings")
        self.raw_cmd.setToolTip("Extra robocopy flags - appended on top of GUI settings")
        self.raw.content_layout.addWidget(self.raw_cmd)

        scroll_layout.addWidget(self.raw)

        scroll_layout.addStretch()

        scroll_content.setLayout(scroll_layout)
        scroll.setWidget(scroll_content)

        main.addWidget(scroll)

        # -----------------------------
        # COMMAND PREVIEW
        # -----------------------------
        preview_row = QHBoxLayout()
        preview_row.setSpacing(8)
        preview_label = QLabel("Command:")
        preview_label.setStyleSheet("font-weight: bold; color: #569cd6;")
        preview_row.addWidget(preview_label)

        self.cmd_preview = QLineEdit()
        self.cmd_preview.setReadOnly(True)
        self.cmd_preview.setPlaceholderText("Adjust any setting above — the command updates in real time")
        self.cmd_preview.setToolTip("Generated robocopy command line based on current settings (auto-updates)")
        self.cmd_preview.setStyleSheet(
            "QLineEdit { background-color: #1e1e1e; color: #6a9955; border: 1px solid #3c3c3c; "
            "border-radius: 4px; padding: 5px 8px; font-family: Consolas, monospace; font-size: 12px; }"
        )
        preview_row.addWidget(self.cmd_preview, 1)

        main.addLayout(preview_row)

        # -----------------------------
        # OK / CANCEL
        # -----------------------------
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.ok_btn = QPushButton("OK")
        self.ok_btn.setToolTip("Apply settings and close")
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setToolTip("Discard changes")
        self.cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(self.ok_btn)
        btn_row.addSpacing(8)
        btn_row.addWidget(self.cancel_btn)
        main.addLayout(btn_row)

        self.setLayout(main)

        self._connect_preview_signals()

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

    def pick_file(self, line_edit):
        path, _ = QFileDialog.getSaveFileName(self)
        if path:
            line_edit.setText(path)

    # -----------------------------
    # PREVIEW
    # -----------------------------
    def preview_command(self):
        cfg = self._collect_config(dry=False)
        cmd = self.core.build_command(cfg)
        self.cmd_preview.setText(" ".join(cmd))

    def _connect_preview_signals(self):
        for w in self.findChildren(QLineEdit):
            w.textChanged.connect(self.preview_command)
        for w in self.findChildren(QSpinBox):
            w.valueChanged.connect(self.preview_command)
        for w in self.findChildren(QCheckBox):
            w.stateChanged.connect(self.preview_command)
        self.sparse_combo.currentIndexChanged.connect(self.preview_command)
        self.mode_btns.group.idClicked.connect(self.preview_command)
        self.subdir_btns.group.idClicked.connect(self.preview_command)
        self.preview_command()

    # -----------------------------
    # LOAD CONFIG (from preset)
    # -----------------------------
    def load_config(self, cfg):
        modes = ["copy", "mirror", "purge", "move", "moveall"]
        mode_val = cfg.get("mode", "copy")
        if mode_val in modes:
            idx = modes.index(mode_val)
            for btn in self.mode_btns.group.buttons():
                if self.mode_btns.group.id(btn) == idx:
                    btn.setChecked(True)
                    break

        subdirs = ["none", "s", "e"]
        sub_val = cfg.get("subdirs", "e")
        if sub_val in subdirs:
            idx = subdirs.index(sub_val)
            for btn in self.subdir_btns.group.buttons():
                if self.subdir_btns.group.id(btn) == idx:
                    btn.setChecked(True)
                    break

        self.mt.setValue(cfg.get("mt", 16))
        self.retries.setValue(cfg.get("retries", 2))
        self.wait.setValue(cfg.get("wait", 1))

        self.chk_z.setChecked(cfg.get("z", False))
        self.chk_b.setChecked(cfg.get("b", False))
        self.chk_zb.setChecked(cfg.get("zb", False))
        self.chk_j.setChecked(cfg.get("j", False))
        self.chk_efsraw.setChecked(cfg.get("efsraw", False))
        self.copy_flags.setText(cfg.get("copy_flags", ""))
        self.dcopy_flags.setText(cfg.get("dcopy_flags", ""))
        self.chk_sec.setChecked(cfg.get("sec", False))
        self.chk_copyall.setChecked(cfg.get("copyall", False))
        self.chk_nocopy.setChecked(cfg.get("nocopy", False))
        self.chk_secfix.setChecked(cfg.get("secfix", False))
        self.chk_timfix.setChecked(cfg.get("timfix", False))
        self.add_attr.setText(cfg.get("add_attr", ""))
        self.remove_attr.setText(cfg.get("remove_attr", ""))
        self.chk_create.setChecked(cfg.get("create", False))
        self.chk_fat.setChecked(cfg.get("fat", False))
        self.chk_no256.setChecked(cfg.get("no256", False))
        self.chk_sj.setChecked(cfg.get("sj", False))
        self.chk_sl.setChecked(cfg.get("sl", False))
        self.chk_nodcopy.setChecked(cfg.get("nodcopy", False))
        self.chk_nooffload.setChecked(cfg.get("nooffload", False))
        self.chk_compress.setChecked(cfg.get("compress", False))
        self.chk_noclone.setChecked(cfg.get("noclone", False))

        sparse = cfg.get("sparse", "")
        if sparse == "y":
            self.sparse_combo.setCurrentIndex(1)
        elif sparse == "n":
            self.sparse_combo.setCurrentIndex(2)
        else:
            self.sparse_combo.setCurrentIndex(0)

        self.lev.setValue(cfg.get("lev", 0))
        self.mon.setValue(cfg.get("mon", 0))
        self.mot.setValue(cfg.get("mot", 0))
        self.rh.setText(cfg.get("rh", ""))
        self.chk_pf.setChecked(cfg.get("pf", False))
        self.ipg.setValue(cfg.get("ipg", 0))

        self.iomaxsize.setText(cfg.get("iomaxsize", ""))
        self.iorate.setText(cfg.get("iorate", ""))
        self.threshold.setText(cfg.get("threshold", ""))

        self.chk_archive_a.setChecked(cfg.get("archive_a", False))
        self.chk_archive_m.setChecked(cfg.get("archive_m", False))
        self.include_attr.setText(cfg.get("include_attr", ""))
        self.exclude_attr.setText(cfg.get("exclude_attr", ""))
        self.exclude_files.setText(cfg.get("exclude_files", ""))
        self.exclude_dirs.setText(cfg.get("exclude_dirs", ""))
        self.chk_xc.setChecked(cfg.get("xc", False))
        self.chk_xn.setChecked(cfg.get("xn", False))
        self.chk_xo.setChecked(cfg.get("xo", False))
        self.chk_xx.setChecked(cfg.get("xx", False))
        self.chk_xl.setChecked(cfg.get("xl", False))
        self.chk_im.setChecked(cfg.get("im", False))
        self.chk_is.setChecked(cfg.get("is_same", False))
        self.chk_it.setChecked(cfg.get("it", False))
        self.max_size.setValue(cfg.get("max_size", 0))
        self.min_size.setValue(cfg.get("min_size", 0))
        self.max_age.setValue(cfg.get("max_age", 0))
        self.min_age.setValue(cfg.get("min_age", 0))
        self.max_lad.setValue(cfg.get("max_lad", 0))
        self.min_lad.setValue(cfg.get("min_lad", 0))
        self.chk_xj.setChecked(cfg.get("xj", False))
        self.chk_fft.setChecked(cfg.get("fft", False))
        self.chk_dst.setChecked(cfg.get("dst_comp", False))
        self.chk_xjd.setChecked(cfg.get("xjd", False))
        self.chk_xjf.setChecked(cfg.get("xjf", False))

        self.chk_reg.setChecked(cfg.get("reg", False))
        self.chk_tbd.setChecked(cfg.get("tbd", False))
        self.chk_lfsm.setChecked(cfg.get("lfsm", False))
        self.lfsm_size.setText(cfg.get("lfsm_size", ""))

        self.chk_list.setChecked(cfg.get("list_only", False))
        self.chk_xreport.setChecked(cfg.get("x_report", False))
        self.chk_v.setChecked(cfg.get("v", False))
        self.chk_ts.setChecked(cfg.get("ts", False))
        self.chk_fp.setChecked(cfg.get("fp", False))
        self.chk_bytes.setChecked(cfg.get("bytes", False))
        self.chk_ns.setChecked(cfg.get("ns", False))
        self.chk_nc.setChecked(cfg.get("nc", False))
        self.chk_nfl.setChecked(cfg.get("nfl", False))
        self.chk_ndl.setChecked(cfg.get("ndl", False))
        self.chk_eta.setChecked(cfg.get("eta", False))
        self.chk_njh.setChecked(cfg.get("njh", False))
        self.chk_njs.setChecked(cfg.get("njs", False))
        self.chk_unicode.setChecked(cfg.get("unicode", False))
        self.chk_log_tee.setChecked(cfg.get("log_tee", False))
        self.log_file.setText(cfg.get("log_file", ""))
        self.log_append_file.setText(cfg.get("log_append_file", ""))
        self.unilog_file.setText(cfg.get("unilog_file", ""))
        self.unilog_append_file.setText(cfg.get("unilog_append_file", ""))

        self.job_name.setText(cfg.get("job_name", ""))
        self.save_name.setText(cfg.get("save_name", ""))
        self.chk_quit.setChecked(cfg.get("quit", False))
        self.chk_nosd.setChecked(cfg.get("nosd", False))
        self.chk_nodd.setChecked(cfg.get("nodd", False))
        self.if_files.setText(cfg.get("if_files", ""))

    def _collect_config(self, dry=False):
        modes = ["copy", "mirror", "purge", "move", "moveall"]
        subdirs = ["none", "s", "e"]

        sparse_val = self.sparse_combo.currentIndex()
        sparse = ""
        if sparse_val == 1:
            sparse = "y"
        elif sparse_val == 2:
            sparse = "n"

        return {
            "src": "", "dst": "",
            "mode": modes[self.mode_btns.group.checkedId()],
            "subdirs": subdirs[self.subdir_btns.group.checkedId()],
            "mt": self.mt.value(),
            "retries": self.retries.value(),
            "wait": self.wait.value(),
            "dry_run": dry,

            "z": self.chk_z.isChecked(),
            "b": self.chk_b.isChecked(),
            "zb": self.chk_zb.isChecked(),
            "j": self.chk_j.isChecked(),
            "efsraw": self.chk_efsraw.isChecked(),
            "copy_flags": self.copy_flags.text(),
            "dcopy_flags": self.dcopy_flags.text(),
            "sec": self.chk_sec.isChecked(),
            "copyall": self.chk_copyall.isChecked(),
            "nocopy": self.chk_nocopy.isChecked(),
            "secfix": self.chk_secfix.isChecked(),
            "timfix": self.chk_timfix.isChecked(),
            "add_attr": self.add_attr.text(),
            "remove_attr": self.remove_attr.text(),
            "create": self.chk_create.isChecked(),
            "fat": self.chk_fat.isChecked(),
            "no256": self.chk_no256.isChecked(),
            "sj": self.chk_sj.isChecked(),
            "sl": self.chk_sl.isChecked(),
            "nodcopy": self.chk_nodcopy.isChecked(),
            "nooffload": self.chk_nooffload.isChecked(),
            "compress": self.chk_compress.isChecked(),
            "noclone": self.chk_noclone.isChecked(),
            "sparse": sparse,
            "lev": self.lev.value(),
            "mon": self.mon.value(),
            "mot": self.mot.value(),
            "rh": self.rh.text(),
            "pf": self.chk_pf.isChecked(),
            "ipg": self.ipg.value(),

            "iomaxsize": self.iomaxsize.text(),
            "iorate": self.iorate.text(),
            "threshold": self.threshold.text(),

            "archive_a": self.chk_archive_a.isChecked(),
            "archive_m": self.chk_archive_m.isChecked(),
            "include_attr": self.include_attr.text(),
            "exclude_attr": self.exclude_attr.text(),
            "exclude_files": self.exclude_files.text(),
            "exclude_dirs": self.exclude_dirs.text(),
            "xc": self.chk_xc.isChecked(),
            "xn": self.chk_xn.isChecked(),
            "xo": self.chk_xo.isChecked(),
            "xx": self.chk_xx.isChecked(),
            "xl": self.chk_xl.isChecked(),
            "im": self.chk_im.isChecked(),
            "is_same": self.chk_is.isChecked(),
            "it": self.chk_it.isChecked(),
            "max_size": self.max_size.value(),
            "min_size": self.min_size.value(),
            "max_age": self.max_age.value(),
            "min_age": self.min_age.value(),
            "max_lad": self.max_lad.value(),
            "min_lad": self.min_lad.value(),
            "xj": self.chk_xj.isChecked(),
            "fft": self.chk_fft.isChecked(),
            "dst_comp": self.chk_dst.isChecked(),
            "xjd": self.chk_xjd.isChecked(),
            "xjf": self.chk_xjf.isChecked(),

            "reg": self.chk_reg.isChecked(),
            "tbd": self.chk_tbd.isChecked(),
            "lfsm": self.chk_lfsm.isChecked(),
            "lfsm_size": self.lfsm_size.text(),

            "list_only": self.chk_list.isChecked(),
            "x_report": self.chk_xreport.isChecked(),
            "v": self.chk_v.isChecked(),
            "ts": self.chk_ts.isChecked(),
            "fp": self.chk_fp.isChecked(),
            "bytes": self.chk_bytes.isChecked(),
            "ns": self.chk_ns.isChecked(),
            "nc": self.chk_nc.isChecked(),
            "nfl": self.chk_nfl.isChecked(),
            "ndl": self.chk_ndl.isChecked(),
            "eta": self.chk_eta.isChecked(),
            "njh": self.chk_njh.isChecked(),
            "njs": self.chk_njs.isChecked(),
            "unicode": self.chk_unicode.isChecked(),
            "log_tee": self.chk_log_tee.isChecked(),
            "log_file": self.log_file.text(),
            "log_append_file": self.log_append_file.text(),
            "unilog_file": self.unilog_file.text(),
            "unilog_append_file": self.unilog_append_file.text(),

            "job_name": self.job_name.text(),
            "save_name": self.save_name.text(),
            "quit": self.chk_quit.isChecked(),
            "nosd": self.chk_nosd.isChecked(),
            "nodd": self.chk_nodd.isChecked(),
            "if_files": self.if_files.text(),
        }

class RunPage(QWidget):
    go_back = pyqtSignal()

    def __init__(self, core):
        super().__init__()
        self.core = core
        self._build_ui()

    def _build_ui(self):
        main = QVBoxLayout()
        main.setSpacing(12)
        main.setContentsMargins(12, 12, 12, 12)

        # Title
        title = QLabel("Execute Robocopy")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #d4d4d4;")
        main.addWidget(title)

        # Command preview
        preview_label = QLabel("Command:")
        preview_label.setStyleSheet("font-weight: bold; color: #569cd6;")
        main.addWidget(preview_label)

        self.cmd_preview = QLineEdit()
        self.cmd_preview.setReadOnly(True)
        self.cmd_preview.setPlaceholderText("No command configured yet")
        self.cmd_preview.setStyleSheet(
            "QLineEdit { background-color: #1e1e1e; color: #6a9955; border: 1px solid #3c3c3c; "
            "border-radius: 4px; padding: 5px 8px; font-family: Consolas, monospace; font-size: 12px; }"
        )
        main.addWidget(self.cmd_preview)

        # Log output
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setToolTip("Robocopy command output appears here")
        self.log.setStyleSheet(
            "QTextEdit { background-color: #0d0d0d; color: #d4d4d4; border: 1px solid #3c3c3c; "
            "border-radius: 4px; padding: 8px; font-family: Consolas, monospace; font-size: 12px; }"
        )
        main.addWidget(self.log, 1)

        # Action buttons
        actions = QHBoxLayout()
        actions.setSpacing(8)

        self.start_btn = QPushButton("\u25b6  START")
        self.start_btn.setToolTip("Begin the robocopy operation")
        self.stop_btn = QPushButton("\u25a0  STOP")
        self.stop_btn.setToolTip("Stop the currently running robocopy process")
        self.dry_btn = QPushButton("\u25c9  DRY RUN")
        self.dry_btn.setToolTip("Simulate - show what would be copied without actually copying (/L)")

        btn_common = "padding: 8px 24px; font-size: 14px; border-radius: 4px; font-weight: bold;"
        self.start_btn.setStyleSheet(
            f"QPushButton {{ background-color: #0e639c; color: white; border: none; {btn_common} }}"
            f"QPushButton:hover {{ background-color: #1177bb; }}"
            f"QPushButton:pressed {{ background-color: #094771; }}"
        )
        self.stop_btn.setStyleSheet(
            f"QPushButton {{ background-color: #3c3c3c; color: #d4d4d4; border: 1px solid #555555; {btn_common} }}"
            f"QPushButton:hover {{ background-color: #4a4a4a; }}"
            f"QPushButton:pressed {{ background-color: #2d2d2d; }}"
        )
        self.dry_btn.setStyleSheet(
            f"QPushButton {{ background-color: #2d2d2d; color: #d4d4d4; border: 1px solid #555555; {btn_common} }}"
            f"QPushButton:hover {{ background-color: #3c3c3c; }}"
            f"QPushButton:pressed {{ background-color: #1e1e1e; }}"
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

        # Cancel button
        cancel_row = QHBoxLayout()
        self.cancel_btn = QPushButton("\u2190  Back")
        self.cancel_btn.setToolTip("Return to setup page")
        self.cancel_btn.setStyleSheet(
            "QPushButton { background-color: #3c3c3c; color: #d4d4d4; border: 1px solid #555555; "
            "padding: 8px 24px; font-size: 13px; border-radius: 4px; }"
            "QPushButton:hover { background-color: #4a4a4a; }"
        )
        self.cancel_btn.clicked.connect(self.go_back.emit)
        cancel_row.addWidget(self.cancel_btn)
        cancel_row.addStretch()
        main.addLayout(cancel_row)

        self.setLayout(main)

    def set_config(self, cfg):
        self._cfg = cfg
        cmd = self.core.build_command(cfg)
        self.cmd_preview.setText(" ".join(cmd))

    def run(self):
        self.execute(dry=False)

    def dry_run(self):
        self.execute(dry=True)

    def stop(self):
        self.core.stop()
        self.log.append("Stopped process\n")

    def execute(self, dry=False):
        cfg = dict(self._cfg)
        if dry:
            cfg["dry_run"] = True
        cmd = self.core.build_command(cfg)
        if not cmd:
            self.log.append("No command to run\n")
            return

        self.log.append("Running:\n" + " ".join(cmd) + "\n\n")

        def out(text, progress=False):
            text = text.strip()
            if not text:
                return
            if progress:
                cursor = self.log.textCursor()
                cursor.movePosition(cursor.MoveOperation.End)
                cursor.movePosition(cursor.MoveOperation.StartOfLine, cursor.MoveMode.KeepAnchor)
                cursor.removeSelectedText()
                cursor.insertText(text)
            else:
                self.log.append(text)

        code = self.core.run(cmd, out)
        self.log.append(f"\nFinished (code {code})\n")


class RoboGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("RoboGUI - Robocopy Manager")
        self.resize(1050, 760)
        self.setStyleSheet(DARK_CSS)

        icon_path = resource_path("..\\icon\\robogui.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.core = RoboCore()
        self._current_cfg = dict(DEFAULT_CFG)
        self._dialog = None

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Page 0 - Setup
        self.presets_page = PresetsPage(self.core)
        self.presets_page.adv_btn.clicked.connect(self._open_full_controls)
        self.presets_page.preset_selected.connect(self._on_preset)
        self.presets_page.next_clicked.connect(self._go_to_run)
        self.stack.addWidget(self.presets_page)

        # Page 1 - Run
        self.run_page = RunPage(self.core)
        self.run_page.go_back.connect(self._go_to_setup)
        self.stack.addWidget(self.run_page)

        self._sync_preset_paths()
        self.stack.setCurrentIndex(0)

    def _sync_preset_paths(self):
        self.presets_page.src_input.textChanged.connect(self._update_preview)
        self.presets_page.dst_input.textChanged.connect(self._update_preview)

    def _update_preview(self):
        merged = dict(self._current_cfg)
        merged["src"] = self.presets_page.src_input.text()
        merged["dst"] = self.presets_page.dst_input.text()
        cmd = self.core.build_command(merged)
        self.presets_page.cmd_preview.setText(" ".join(cmd))

    def _on_preset(self, cfg):
        self._current_cfg = cfg
        self._current_cfg["src"] = self.presets_page.src_input.text()
        self._current_cfg["dst"] = self.presets_page.dst_input.text()
        self._update_preview()

    def _open_full_controls(self):
        if self._dialog is None:
            self._dialog = FullControlsDialog(self.core, self)
        self._dialog.load_config(self._current_cfg)
        if self._dialog.exec() == QDialog.DialogCode.Accepted:
            collected = self._dialog._collect_config(dry=False)
            self._current_cfg.update(collected)
            self._current_cfg["src"] = self.presets_page.src_input.text()
            self._current_cfg["dst"] = self.presets_page.dst_input.text()
            self._update_preview()

    def _go_to_run(self):
        cfg = dict(self._current_cfg)
        cfg["src"] = self.presets_page.src_input.text()
        cfg["dst"] = self.presets_page.dst_input.text()
        self.run_page.set_config(cfg)
        self.run_page.log.clear()
        self.stack.setCurrentIndex(1)

    def _go_to_setup(self):
        self.stack.setCurrentIndex(0)
