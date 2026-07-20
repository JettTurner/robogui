import os
from datetime import datetime

from PyQt6.QtCore import QObject, QThread, pyqtSignal


class _Worker(QThread):
    progress = pyqtSignal(str, int, int)
    finished = pyqtSignal(dict, dict)
    error = pyqtSignal(str)

    def __init__(self, src_path, dst_path, cfg):
        super().__init__()
        self.src_path = src_path
        self.dst_path = dst_path
        self.cfg = cfg or {}
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def run(self):
        try:
            src_files = self._scan_directory(self.src_path, "source")
            if self._cancelled:
                return
            dst_files = self._scan_directory(self.dst_path, "destination")
            if self._cancelled:
                return
            self.finished.emit(src_files, dst_files)
        except Exception as e:
            if not self._cancelled:
                self.error.emit(str(e))

    def _count_entries(self, path):
        count = 0
        try:
            for entry in os.scandir(path):
                count += 1
                if entry.is_dir(follow_symlinks=False):
                    count += self._count_entries(entry.path)
        except PermissionError:
            pass
        return count

    def _scan_directory(self, path, label):
        if not path or not os.path.isdir(path):
            return {}

        max_lev = self.cfg.get("lev", 0)
        exclude_files = self.cfg.get("exclude_files", "").strip().split() if self.cfg.get("exclude_files") else []
        exclude_dirs = self.cfg.get("exclude_dirs", "").strip().split() if self.cfg.get("exclude_dirs") else []

        self.progress.emit(f"Counting {label}...", 0, 0)
        total = self._count_entries(path)
        self.progress.emit(f"Scanning {label}...", 0, max(total, 1))

        result = {}
        scanned = [0]

        def _walk(current, rel, depth):
            if self._cancelled:
                return
            try:
                entries = list(os.scandir(current))
            except PermissionError:
                return

            for entry in entries:
                if self._cancelled:
                    return
                name = entry.name
                entry_rel = os.path.join(rel, name) if rel else name

                if entry.is_dir(follow_symlinks=False):
                    if name.upper() in (d.upper() for d in exclude_dirs):
                        continue
                    result[entry_rel] = {
                        "name": name,
                        "size": 0,
                        "modified": datetime.fromtimestamp(entry.stat().st_mtime),
                        "is_dir": True,
                    }
                    scanned[0] += 1
                    if scanned[0] % 20 == 0:
                        self.progress.emit(
                            f"Scanning: {entry.path}",
                            scanned[0],
                            total,
                        )
                    if max_lev == 0 or depth < max_lev:
                        _walk(entry.path, entry_rel, depth + 1)
                elif entry.is_file(follow_symlinks=False):
                    if name.upper() in (f.upper() for f in exclude_files):
                        continue
                    stat = entry.stat()
                    result[entry_rel] = {
                        "name": name,
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime),
                        "is_dir": False,
                    }
                    scanned[0] += 1
                    if scanned[0] % 20 == 0:
                        self.progress.emit(
                            f"Scanning: {entry.path}",
                            scanned[0],
                            total,
                        )

        _walk(path, "", 0)
        self.progress.emit(f"Finished {label}", total, total)
        return result


class DirectoryScanner(QObject):
    progress = pyqtSignal(str, int, int)
    finished = pyqtSignal(dict, dict)
    error = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._worker = None

    def start_scan(self, src_path, dst_path, cfg):
        self.cancel_scan()

        self._worker = _Worker(src_path, dst_path, cfg)
        self._worker.progress.connect(self.progress.emit)
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self.error.emit)
        self._worker.finished.connect(self._cleanup)
        self._worker.error.connect(self._cleanup)
        self._worker.start()

    def cancel_scan(self):
        if self._worker and self._worker.isRunning():
            self._worker.cancel()
            self._worker.wait(2000)
        self._worker = None

    def _on_finished(self, src_files, dst_files):
        self.finished.emit(src_files, dst_files)

    def _cleanup(self):
        if self._worker:
            self._worker.deleteLater()
            self._worker = None
