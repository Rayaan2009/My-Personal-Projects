import json
import os
import shlex
import subprocess
import sys
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QApplication,
    QAbstractItemView,
    QCheckBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QHeaderView,
)


# -----------------------------
# Helpers
# -----------------------------
def run_cmd(cmd: List[str]) -> Tuple[int, str, str]:
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = p.communicate()
    return p.returncode, out, err


def ffprobe_streams(path: str) -> Dict:
    cmd = [
        "ffprobe",
        "-v", "error",
        "-print_format", "json",
        "-show_format",
        "-show_streams",
        path,
    ]
    rc, out, err = run_cmd(cmd)
    if rc != 0:
        raise RuntimeError(f"ffprobe failed:\n{err.strip()}")
    return json.loads(out)


def safe_str(v: Optional[str]) -> str:
    return v if v is not None else ""


def guess_output_path(input_path: str) -> str:
    base, ext = os.path.splitext(input_path)
    return f"{base}_edited{ext or '.mkv'}"


# -----------------------------
# Data model
# -----------------------------
@dataclass
class Track:
    # ffprobe
    abs_stream_index: int          # absolute index in input (ffmpeg -map 0:<abs>)
    track_type: str               # "audio" or "subtitle"
    type_idx_in_input: int        # index within type in input (0:a:N / 0:s:N)
    codec: str = ""
    channels: str = ""
    language: str = ""
    title: str = ""
    is_default: bool = False
    is_forced: bool = False

    # UI edits
    marked_delete: bool = False
    edit_language: str = ""
    edit_title: str = ""
    edit_default: bool = False


# -----------------------------
# Drag-drop table
# -----------------------------
class ReorderTable(QTableWidget):
    rows_reordered = Signal()

    def dropEvent(self, event):
        super().dropEvent(event)
        self.rows_reordered.emit()


# -----------------------------
# Main Window
# -----------------------------
class MainWindow(QMainWindow):
    COL_DELETE = 0
    COL_TYPE = 1
    COL_INIDX = 2
    COL_CODEC = 3
    COL_CHANNELS = 4
    COL_LANG = 5
    COL_TITLE = 6
    COL_DEFAULT = 7
    COL_FORCED = 8

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Track Editor v2 — Reorder Audio/Subtitles (Remux)")
        self.setMinimumSize(1100, 650)

        self.input_path: Optional[str] = None

        # We keep ALL streams info for correct mapping.
        self.input_video_abs: List[int] = []
        self.input_other_abs: List[int] = []  # data/attachment/unknown etc.

        # Table only shows these (reorderable)
        self.tracks: List[Track] = []

        # UI
        self.lbl_file = QLabel("No file selected.")
        self.btn_pick = QPushButton("Select MKV…")
        self.btn_pick.clicked.connect(self.pick_file)

        self.btn_reload = QPushButton("Reload")
        self.btn_reload.clicked.connect(self.reload_probe)
        self.btn_reload.setEnabled(False)

        self.btn_default_audio = QPushButton("Set selected DEFAULT (Audio)")
        self.btn_default_audio.clicked.connect(lambda: self.set_default_for_selected("audio"))
        self.btn_default_audio.setEnabled(False)

        self.btn_default_sub = QPushButton("Set selected DEFAULT (Subtitles)")
        self.btn_default_sub.clicked.connect(lambda: self.set_default_for_selected("subtitle"))
        self.btn_default_sub.setEnabled(False)

        self.btn_save_as = QPushButton("Save As… (Remux)")
        self.btn_save_as.clicked.connect(self.save_as)
        self.btn_save_as.setEnabled(False)

        self.btn_up = QPushButton("Move Up")
        self.btn_down = QPushButton("Move Down")
        self.btn_up.clicked.connect(lambda: self.move_selected(-1))
        self.btn_down.clicked.connect(lambda: self.move_selected(+1))
        self.btn_up.setEnabled(False)
        self.btn_down.setEnabled(False)

        # Table
        self.table = ReorderTable(0, 9)
        self.table.setHorizontalHeaderLabels([
            "Delete",
            "Type",
            "Input #",
            "Codec",
            "Ch",
            "Language (editable)",
            "Title (editable)",
            "Default",
            "Forced",
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.SelectedClicked)

        # Drag-drop reorder
        self.table.setDragDropMode(QAbstractItemView.InternalMove)
        self.table.setDefaultDropAction(Qt.MoveAction)
        self.table.setDragEnabled(True)
        self.table.setDropIndicatorShown(True)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.rows_reordered.connect(self.sync_model_from_table_order)

        self.table.itemChanged.connect(self.on_item_changed)

        # Layout
        top = QHBoxLayout()
        top.addWidget(self.btn_pick)
        top.addWidget(self.btn_reload)
        top.addStretch(1)
        top.addWidget(self.btn_up)
        top.addWidget(self.btn_down)
        top.addWidget(self.btn_default_audio)
        top.addWidget(self.btn_default_sub)
        top.addWidget(self.btn_save_as)

        root = QVBoxLayout()
        root.addLayout(top)
        root.addWidget(self.lbl_file)
        root.addWidget(self.table)

        w = QWidget()
        w.setLayout(root)
        self.setCentralWidget(w)

        self._guard = False

    # -----------------------------
    # File / probe
    # -----------------------------
    def pick_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select a video file",
            "",
            "Video files (*.mkv *.mp4 *.mov *.m4v *.avi *.webm *.ts *.m2ts);;All files (*.*)"
        )
        if not path:
            return
        self.input_path = path
        self.lbl_file.setText(path)
        self.btn_reload.setEnabled(True)
        self.reload_probe()

    def reload_probe(self):
        if not self.input_path:
            return
        try:
            probe = ffprobe_streams(self.input_path)
            self.parse_all_streams(probe)
            self.populate_table()

            enabled = len(self.tracks) > 0
            self.btn_default_audio.setEnabled(enabled)
            self.btn_default_sub.setEnabled(enabled)
            self.btn_save_as.setEnabled(enabled)
            self.btn_up.setEnabled(enabled)
            self.btn_down.setEnabled(enabled)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def parse_all_streams(self, probe: Dict):
        self.input_video_abs.clear()
        self.input_other_abs.clear()
        self.tracks.clear()

        audio_count = 0
        sub_count = 0

        streams = probe.get("streams", []) or []
        for s in streams:
            ctype = safe_str(s.get("codec_type"))
            abs_idx = int(s.get("index"))

            if ctype == "video":
                self.input_video_abs.append(abs_idx)
                continue

            if ctype not in ("audio", "subtitle"):
                # keep other streams in original order
                self.input_other_abs.append(abs_idx)
                continue

            tags = s.get("tags", {}) or {}
            disp = s.get("disposition", {}) or {}

            lang = safe_str(tags.get("language"))
            title = safe_str(tags.get("title"))
            codec = safe_str(s.get("codec_name"))

            is_def = bool(disp.get("default", 0))
            is_forced = bool(disp.get("forced", 0))

            channels = ""
            if ctype == "audio":
                ch = s.get("channels")
                channels = str(ch) if ch is not None else ""

            if ctype == "audio":
                type_idx = audio_count
                audio_count += 1
                ttype = "audio"
            else:
                type_idx = sub_count
                sub_count += 1
                ttype = "subtitle"

            tr = Track(
                abs_stream_index=abs_idx,
                track_type=ttype,
                type_idx_in_input=type_idx,
                codec=codec,
                channels=channels,
                language=lang,
                title=title,
                is_default=is_def,
                is_forced=is_forced,
                marked_delete=False,
                edit_language=lang,
                edit_title=title,
                edit_default=is_def,
            )
            self.tracks.append(tr)

        # preserve original order as in file (already in ffprobe order)

    # -----------------------------
    # Table population / sync
    # -----------------------------
    def populate_table(self):
        self._guard = True
        try:
            self.table.setRowCount(0)
            for tr in self.tracks:
                r = self.table.rowCount()
                self.table.insertRow(r)

                del_cb = QCheckBox()
                del_cb.setChecked(tr.marked_delete)
                del_cb.stateChanged.connect(lambda st, row=r: self.on_delete_toggled(row, st))
                self.table.setCellWidget(r, self.COL_DELETE, del_cb)

                self._set_item(r, self.COL_TYPE, tr.track_type, editable=False)
                self._set_item(r, self.COL_INIDX, f"0:{'a' if tr.track_type=='audio' else 's'}:{tr.type_idx_in_input}", editable=False)
                self._set_item(r, self.COL_CODEC, tr.codec, editable=False)
                self._set_item(r, self.COL_CHANNELS, tr.channels if tr.track_type == "audio" else "-", editable=False)

                self._set_item(r, self.COL_LANG, tr.edit_language, editable=True)
                self._set_item(r, self.COL_TITLE, tr.edit_title, editable=True)

                def_cb = QCheckBox()
                def_cb.setChecked(tr.edit_default)
                def_cb.stateChanged.connect(lambda st, row=r: self.on_default_toggled(row, st))
                self.table.setCellWidget(r, self.COL_DEFAULT, def_cb)

                self._set_item(r, self.COL_FORCED, "Yes" if tr.is_forced else "No", editable=False)

            self.table.resizeColumnsToContents()
        finally:
            self._guard = False

    def _set_item(self, row: int, col: int, text: str, editable: bool):
        it = QTableWidgetItem(text)
        if not editable:
            it.setFlags(it.flags() & ~Qt.ItemIsEditable)
        self.table.setItem(row, col, it)

    def sync_model_from_table_order(self):
        if self._guard:
            return
        # After drag-drop, the visual row order changed.
        # We rebuild self.tracks by reading a stable key from a hidden mapping:
        # easiest: store abs_stream_index as Qt.UserRole in the Type cell item.
        # But we didn't store it initially. We'll do it now in a robust way:
        # We'll reconstruct by reading the Input # column, matching to original items.
        # Since Input # (0:a:N / 0:s:N) can collide across types? It includes type and N, so unique.
        key_to_track = {f"{t.track_type}:{t.type_idx_in_input}": t for t in self.tracks}
        new_tracks: List[Track] = []

        for r in range(self.table.rowCount()):
            ttype = self.table.item(r, self.COL_TYPE).text()
            inidx = self.table.item(r, self.COL_INIDX).text()  # "0:a:N" or "0:s:N"
            # parse N
            n = int(inidx.split(":")[-1])
            key = f"{ttype}:{n}"
            tr = key_to_track.get(key)
            if tr is None:
                continue
            # update edits from UI row
            tr.edit_language = self.table.item(r, self.COL_LANG).text().strip()
            tr.edit_title = self.table.item(r, self.COL_TITLE).text().strip()
            del_cb = self.table.cellWidget(r, self.COL_DELETE)
            def_cb = self.table.cellWidget(r, self.COL_DEFAULT)
            if isinstance(del_cb, QCheckBox):
                tr.marked_delete = del_cb.isChecked()
            if isinstance(def_cb, QCheckBox):
                tr.edit_default = def_cb.isChecked()
            new_tracks.append(tr)

        self.tracks = new_tracks

    # -----------------------------
    # UI actions
    # -----------------------------
    def on_delete_toggled(self, row: int, state: int):
        if row < 0 or row >= len(self.tracks):
            return
        self.tracks[row].marked_delete = (state == Qt.Checked)

    def on_default_toggled(self, row: int, state: int):
        if row < 0 or row >= len(self.tracks):
            return
        self.tracks[row].edit_default = (state == Qt.Checked)

    def on_item_changed(self, item: QTableWidgetItem):
        if self._guard:
            return
        r = item.row()
        c = item.column()
        if r < 0 or r >= len(self.tracks):
            return
        tr = self.tracks[r]
        if c == self.COL_LANG:
            tr.edit_language = item.text().strip()
        elif c == self.COL_TITLE:
            tr.edit_title = item.text().strip()

    def selected_row(self) -> Optional[int]:
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return None
        return rows[0].row()

    def move_selected(self, delta: int):
        r = self.selected_row()
        if r is None:
            return
        new_r = r + delta
        if new_r < 0 or new_r >= self.table.rowCount():
            return

        # swap in model
        self.tracks[r], self.tracks[new_r] = self.tracks[new_r], self.tracks[r]
        # refresh table
        self.populate_table()
        self.table.selectRow(new_r)

    def set_default_for_selected(self, track_type: str):
        r = self.selected_row()
        if r is None:
            QMessageBox.information(self, "Select a track", "Select a row first.")
            return
        tr = self.tracks[r]
        if tr.track_type != track_type:
            QMessageBox.information(self, "Wrong type", f"Select a {track_type} row.")
            return

        # enforce one default per type among NOT-deleted tracks
        for t in self.tracks:
            if t.track_type == track_type and not t.marked_delete:
                t.edit_default = (t is tr)

        self.populate_table()
        self.table.selectRow(r)

    # -----------------------------
    # Remux
    # -----------------------------
    def save_as(self):
        if not self.input_path:
            return

        # ensure model matches current UI order (important after drag-drop)
        self.sync_model_from_table_order()

        out_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save remuxed file as…",
            guess_output_path(self.input_path),
            "Matroska (*.mkv);;All files (*.*)"
        )
        if not out_path:
            return

        try:
            cmd = self.build_ffmpeg_command(self.input_path, out_path)
        except Exception as e:
            QMessageBox.critical(self, "Error building command", str(e))
            return

        preview = " ".join(shlex.quote(x) for x in cmd)
        ok = QMessageBox.question(
            self,
            "Confirm remux",
            "This will create a NEW file (original untouched).\n\nProceed?\n\n"
            f"Command:\n{preview}"
        )
        if ok != QMessageBox.Yes:
            return

        rc, out, err = run_cmd(cmd)
        if rc != 0:
            QMessageBox.critical(self, "FFmpeg failed", err.strip() or out.strip())
            return

        QMessageBox.information(self, "Done", f"Saved:\n{out_path}")

    def build_ffmpeg_command(self, in_path: str, out_path: str) -> List[str]:
        # enforce single default per type (kept tracks only)
        def enforce_single_default(ttype: str):
            kept = [t for t in self.tracks if t.track_type == ttype and not t.marked_delete]
            defaults = [t for t in kept if t.edit_default]
            if len(defaults) <= 1:
                return
            first = defaults[0]
            for t in kept:
                t.edit_default = (t is first)

        enforce_single_default("audio")
        enforce_single_default("subtitle")

        cmd = ["ffmpeg", "-hide_banner", "-y", "-i", in_path]

        # Mapping order:
        # 1) all video streams (original order)
        # 2) audio/subtitle in USER order (excluding deletions)
        # 3) other streams (data/attachments) original order
        maps: List[int] = []
        maps.extend(self.input_video_abs)

        kept_tracks = [t for t in self.tracks if not t.marked_delete]
        maps.extend([t.abs_stream_index for t in kept_tracks])

        maps.extend(self.input_other_abs)

        # add -map 0:<abs>
        for abs_idx in maps:
            cmd += ["-map", f"0:{abs_idx}"]

        # copy streams
        cmd += ["-c", "copy"]

        # compute OUTPUT indices per type (audio/sub) after mapping
        # We count only within the mapped output, in the order we mapped.
        out_audio_idx = 0
        out_sub_idx = 0

        # We mapped video first, then kept_tracks in order. Only kept_tracks affects these indices.
        # For each kept track, assign its output type index
        track_to_out_type_index: Dict[int, int] = {}  # abs_stream_index -> out type index
        for t in kept_tracks:
            if t.track_type == "audio":
                track_to_out_type_index[t.abs_stream_index] = out_audio_idx
                out_audio_idx += 1
            else:
                track_to_out_type_index[t.abs_stream_index] = out_sub_idx
                out_sub_idx += 1

        # metadata updates
        for t in kept_tracks:
            if t.track_type == "audio":
                oi = track_to_out_type_index[t.abs_stream_index]
                if t.edit_language.strip():
                    cmd += [f"-metadata:s:a:{oi}", f"language={t.edit_language.strip()}"]
                if t.edit_title.strip():
                    cmd += [f"-metadata:s:a:{oi}", f"title={t.edit_title.strip()}"]
            else:
                oi = track_to_out_type_index[t.abs_stream_index]
                if t.edit_language.strip():
                    cmd += [f"-metadata:s:s:{oi}", f"language={t.edit_language.strip()}"]
                if t.edit_title.strip():
                    cmd += [f"-metadata:s:s:{oi}", f"title={t.edit_title.strip()}"]

        # disposition default (only if user selected any default for that type)
        def apply_default(ttype: str):
            kept = [t for t in kept_tracks if t.track_type == ttype]
            if not kept:
                return
            chosen = [t for t in kept if t.edit_default]
            if not chosen:
                return  # don't touch defaults
            # clear all
            for t in kept:
                oi = track_to_out_type_index[t.abs_stream_index]
                cmd.append(f"-disposition:{'a' if ttype=='audio' else 's'}:{oi}")
                cmd.append("0")
            # set chosen (unique due to enforcement)
            t = chosen[0]
            oi = track_to_out_type_index[t.abs_stream_index]
            cmd.append(f"-disposition:{'a' if ttype=='audio' else 's'}:{oi}")
            cmd.append("default")

        apply_default("audio")
        apply_default("subtitle")

        cmd.append(out_path)
        return cmd


def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()