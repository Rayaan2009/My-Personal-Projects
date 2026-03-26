# -----------------------------------------------------------------------------
# YouTube Pro Downloader
# Copyright (c) 2025 Rayaan Bin Saifullah. All rights reserved.
# Unauthorized copying of this file, via any medium, is strictly prohibited.
# Proprietary and confidential.
# -----------------------------------------------------------------------------

import os
import glob
import json
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox
from tkinter import ttk
import yt_dlp

# Fancy themed widgets
import ttkbootstrap as tb

APP_NAME = "YouTube Pro Downloader"
APP_AUTHOR = "Rayaan Bin Saifullah"
APP_COPYRIGHT = "© 2025 Rayaan Bin Saifullah - All Rights Reserved"
ALLOW_PERSISTENCE = os.environ.get("YT_PRO_ALLOW_CFG") == "1"
CFG_FILE = os.path.join(os.path.expanduser("~"), ".yt_pro_downloader.json") if ALLOW_PERSISTENCE else None

ABOUT_TEXT = f"""{APP_NAME}
{APP_COPYRIGHT}

This software is proprietary. You may not copy, modify, or redistribute
without express permission from the author.

Libraries used:
• yt-dlp
• ttkbootstrap

Privacy:
• No config, cache, or log files are written unless YT_PRO_ALLOW_CFG=1
"""

# ---------- sensible defaults ----------
def guess_ffmpeg():
    for candidate in (
        "/opt/homebrew/bin/ffmpeg",  # Apple silicon Homebrew
        "/usr/local/bin/ffmpeg",     # Intel Homebrew
        "/usr/bin/ffmpeg",           # Xcode or package manager
    ):
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate
    return ""

_default_base = Path.home() / "Movies" / "YouTube Pro Downloader"
DEFAULTS = {
    "ffmpeg_path": guess_ffmpeg(),
    "out_archival": str(_default_base / "Archival MKV"),
    "out_ios": str(_default_base / "Apple MP4"),
    "user_agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) "
        "Version/17.0 Safari/605.1.15"
    ),
    "playlist_index": True,

    # Embed-only by default (no sidecars)
    "write_subs": False,        # sidecar .vtt off
    "embed_subs": True,         # embed subs into container
    "subs_langs": ["en.*"],     # EN only; avoids auto-translated spam (ja/pt/ru/...)
    "write_thumb": False,       # sidecar image off
    "embed_thumb": True,        # embed cover art

    "write_desc": False,
    "write_infojson": False,

    "sponsorblock_mark": False,
    "sponsorblock_remove": False,
    "split_chapters": False,

    "rate_limit": "",
    "proxy": "",

    # Optional external downloader
    "use_aria2c": False,
    "aria2c_conns": 16,
    "aria2c_chunk": "5M",
}
# --------------------------------------

def human_bytes(n):
    if n is None:
        return "?"
    units = ["B","KB","MB","GB","TB"]
    i = 0
    n = float(n)
    while n >= 1024 and i < len(units) - 1:
        n /= 1024.0
        i += 1
    return f"{n:.2f} {units[i]}"

def human_rate(n):
    if n is None:
        return "?"
    return f"{human_bytes(n)}/s"

def human_eta(seconds):
    if seconds is None:
        return "?"
    seconds = int(seconds)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return f"{h:d}:{m:02d}:{s:02d}" if h else f"{m:d}:{s:02d}"

def cleanup_vtt(outdir):
    # If we didn’t ask to save subs, bin any stray .vtt that might appear after errors
    try:
        for p in glob.glob(os.path.join(outdir, "*.vtt")):
            try: os.remove(p)
            except: pass
    except:  # being extra chill
        pass
# ---------------------------------------------------

def load_cfg():
    # Privacy-first: only read from disk if explicitly opted in
    if ALLOW_PERSISTENCE and CFG_FILE and os.path.isfile(CFG_FILE):
        try:
            with open(CFG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return {**DEFAULTS, **data}
        except Exception:
            return DEFAULTS.copy()
    return DEFAULTS.copy()

def save_cfg(cfg):
    # By default do not write anything to disk; opt in via YT_PRO_ALLOW_CFG=1
    if not (ALLOW_PERSISTENCE and CFG_FILE):
        return
    try:
        with open(CFG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
    except Exception:
        pass

# Pre-scan so we know if it’s a playlist or a lone ranger
def preflight_list(url):
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "extract_flat": True,
        "cachedir": False,  # privacy: do not create yt-dlp cache
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
    items = []
    if not info:
        return [(url, "")], 1, ""
    if "entries" in info and info["entries"]:
        for e in info["entries"]:
            if not e: continue
            item_url = e.get("url") or e.get("webpage_url") or e.get("original_url")
            title = e.get("title") or ""
            if item_url: items.append((item_url, title))
        return items, len(items), info.get("title") or ""
    one_url = info.get("webpage_url") or info.get("original_url") or url
    return [(one_url, info.get("title") or "")], 1, info.get("title") or ""

# Build yt-dlp options
def build_common_opts(cfg, outdir, log_widget, pbar, status_lbl, overall_lbl,
                      cur_idx, total_count, current_title, simulate=False):
    out_tmpl = r"%(playlist_index)02d - %(title)s.%(ext)s" if cfg["playlist_index"] else r"%(title)s.%(ext)s"
    os.makedirs(outdir, exist_ok=True)

    class TkLogger:
        def debug(self, msg):
            if msg is None: return
            log_widget.after(0, lambda: append_log(log_widget, str(msg)))
        def warning(self, msg):
            if msg is None: return
            log_widget.after(0, lambda: append_log(log_widget, "WARN: " + str(msg)))
        def error(self, msg):
            if msg is None: return
            log_widget.after(0, lambda: append_log(log_widget, "ERROR: " + str(msg)))

    def make_hook():
        idx, total = cur_idx, total_count
        title = (current_title or "").strip()
        def hook(d):
            st = d.get("status")
            total_bytes = d.get("total_bytes") or d.get("total_bytes_estimate")
            downloaded = d.get("downloaded_bytes")
            speed = d.get("speed")
            eta = d.get("eta")
            overall_lbl.after(0, lambda: overall_lbl.configure(
                text=f"Item {idx} of {total}  •  {title}" if total > 1 else f"{title}"
            ))
            if st == "downloading":
                if total_bytes and total_bytes > 0:
                    pct = max(0.0, min(100.0, (downloaded or 0) * 100.0 / total_bytes))
                    pbar.after(0, lambda: (pbar.configure(mode="determinate", maximum=100),
                                           pbar.configure(value=pct)))
                    status_lbl.after(0, lambda: status_lbl.configure(
                        text=f"{pct:5.1f}%  •  {human_bytes(downloaded)} / {human_bytes(total_bytes)}  •  {human_rate(speed)}  •  ETA {human_eta(eta)}"
                    ))
                else:
                    pbar.after(0, lambda: (pbar.configure(mode="indeterminate"), pbar.start(12)))
                    status_lbl.after(0, lambda: status_lbl.configure(
                        text=f"{human_bytes(downloaded)} downloaded  •  {human_rate(speed)}"
                    ))
            elif st == "finished":
                pbar.after(0, lambda: (pbar.configure(mode="determinate", value=100)))
                status_lbl.after(0, lambda: status_lbl.configure(text="Download complete. Finalizing (merge/mux)…"))
        return hook

    opts = {
        # Networking / stability
        "http_chunk_size": 104857600,
        "concurrent_fragments": 6,
        "retries": 50,
        "fragment_retries": 20,
        "skip_unavailable_fragments": True,
        "continuedl": True,
        "sleep_interval_requests": 5,
        "max_sleep_interval_requests": 15,
        "throttledratelimit": (cfg["rate_limit"] or None),
        "proxy": (cfg["proxy"] or None),

        # Housekeeping
        "ignoreerrors": "only_download",
        "restrictfilenames": True,
        "nooverwrites": False,
        "overwrites": False,
        "writedescription": cfg["write_desc"],
        "writeinfojson": cfg["write_infojson"],

        # NO sidecars unless explicitly enabled
        "writesubtitles": cfg["write_subs"],
        "writethumbnail": cfg["write_thumb"],
        "embedsubtitles": cfg["embed_subs"],
        "embedthumbnail": cfg["embed_thumb"],
        "subtitleslangs": cfg["subs_langs"],
        "writeautomaticsub": True,   # will use auto EN only if no human EN; no translations since subs_langs=EN only

        # SponsorBlock / chapters
        "sponsorblock_mark": ["all"] if cfg["sponsorblock_mark"] or cfg["sponsorblock_remove"] else [],
        "sponsorblock_remove": ["all"] if cfg["sponsorblock_remove"] else [],
        "split_chapters": cfg["split_chapters"],

        # Paths, tools, headers
        "outtmpl": os.path.join(outdir, out_tmpl),
        "ffmpeg_location": cfg["ffmpeg_path"] if os.path.isfile(cfg["ffmpeg_path"]) else None,
        "http_headers": {"User-Agent": cfg["user_agent"]},
        "cachedir": False,  # privacy: do not write yt-dlp cache

        # Logging + hooks
        "logger": TkLogger(),
        "progress_with_newline": True,
        "simulate": simulate,
        "verbose": True,
        "progress_hooks": [make_hook()],
    }

    # Optional: aria2c speed-up
    if cfg.get("use_aria2c", False):
        opts["external_downloader"] = "aria2c"
        opts["external_downloader_args"] = {
            "aria2c": [
                f"-x{int(cfg.get('aria2c_conns',16))}",
                f"-k{cfg.get('aria2c_chunk','5M')}",
                "--console-log-level=warn",
                "--summary-interval=0",
            ]
        }
    return opts

def profile_archival(cfg, outdir, log_widget, pbar, status_lbl, overall_lbl, cur_idx, total_count, current_title):
    opts = build_common_opts(cfg, outdir, log_widget, pbar, status_lbl, overall_lbl, cur_idx, total_count, current_title)
    opts.update({
        "format": "bv*+ba/b",
        "format_sort": ["vcodec:av01", "vcodec:vp9", "codec:h264", "res", "br", "fps"],
        "format_sort_force": True,
        "merge_output_format": "mkv",
    })
    return opts

def profile_ios(cfg, outdir, log_widget, pbar, status_lbl, overall_lbl, cur_idx, total_count, current_title):
    opts = build_common_opts(cfg, outdir, log_widget, pbar, status_lbl, overall_lbl, cur_idx, total_count, current_title)
    opts.update({
        # Prefer AVC high → step down smoothly; last resort: progressive MP4
        "format": (
            'bv*[vcodec~="^avc"][height>=2160]+ba[acodec~="^mp4a"]/'
            'bv*[vcodec~="^avc"][height>=1440]+ba[acodec~="^mp4a"]/'
            'bv*[vcodec~="^avc"][height>=1080]+ba[acodec~="^mp4a"]/'
            'bv*[vcodec~="^avc"][height>=720]+ba[acodec~="^mp4a"]/'
            'bv*[vcodec~="^avc"]+ba[acodec~="^mp4a"]/'
            'b[ext=mp4]'
        ),
        "format_sort": ["res", "fps", "br", "vcodec:avc"],
        "format_sort_force": True,
        "merge_output_format": "mp4",
    })
    return opts

def append_log(widget, text):
    widget.insert("end", text.rstrip() + "\n")
    widget.see("end")

# Main runner with threaded preflight + cleanup on errors/success
def run_download(url, mode, cfg, log_widget, btn, pbar, status_lbl, overall_bar, overall_lbl):
    if not url.strip():
        messagebox.showerror(APP_NAME, "Please paste a video/playlist/channel URL.")
        return

    btn.config(state="disabled")
    pbar.configure(mode="determinate", maximum=100, value=0)
    overall_bar.configure(mode="determinate", maximum=100, value=0)
    overall_lbl.configure(text="Scanning… (preflight)")
    status_lbl.configure(text="Starting…")

    def background_preflight():
        try:
            items, total_count, _ = preflight_list(url)
        except Exception as e:
            btn.after(0, lambda: btn.config(state="normal"))
            messagebox.showerror(APP_NAME, f"Could not read the URL:\n{e}")
            return

        if total_count < 1:
            btn.after(0, lambda: btn.config(state="normal"))
            messagebox.showerror(APP_NAME, "No downloadable items found.")
            return

        def task():
            try:
                def do_profile(profile_builder, outdir_label, outdir_path):
                    completed = 0
                    for idx, (item_url, title) in enumerate(items, start=1):
                        safe_title = (title or "").strip()
                        append_log(log_widget, f"\n=== [{outdir_label}] Item {idx}/{total_count}: {safe_title} ===")
                        opts = profile_builder(cfg, outdir_path, log_widget, pbar, status_lbl, overall_lbl, idx, total_count, safe_title)
                        with yt_dlp.YoutubeDL(opts) as ydl:
                            try:
                                ydl.download([item_url])
                            except Exception as e:
                                append_log(log_widget, f"ERROR while downloading subtitles/video: {e}")
                                # Clean any stray .vtt if we didn’t ask to save subs
                                if not cfg.get("write_subs", False):
                                    cleanup_vtt(outdir_path)
                                raise

                        # Clean any stray .vtt after success too (paranoid tidy)
                        if not cfg.get("write_subs", False):
                            cleanup_vtt(outdir_path)

                        completed += 1
                        overall_pct = completed * 100.0 / total_count
                        overall_bar.after(0, lambda v=overall_pct: overall_bar.configure(value=v))
                        overall_lbl.after(0, lambda c=completed: overall_lbl.configure(
                            text=f"Completed {c} of {total_count}"
                        ))

                if mode in ("Archival (MKV)", "Both"):
                    do_profile(lambda *args: profile_archival(*args),
                               "ARCHIVAL MKV", cfg["out_archival"])

                if mode in ("Apple Native (MP4)", "Both"):
                    if mode == "Both":
                        overall_bar.after(0, lambda: overall_bar.configure(value=0))
                        overall_lbl.after(0, lambda: overall_lbl.configure(text="Starting second pass (iOS)…"))
                    do_profile(lambda *args: profile_ios(*args),
                               "iOS MP4", cfg["out_ios"])

                status_lbl.after(0, lambda: status_lbl.configure(text="All done."))
                append_log(log_widget, "\n✓ Done.")
                messagebox.showinfo(APP_NAME, "Download(s) completed.")
            finally:
                btn.after(0, lambda: btn.config(state="normal"))

        threading.Thread(target=task, daemon=True).start()

    threading.Thread(target=background_preflight, daemon=True).start()

def browse_dir(entry_widget):
    path = filedialog.askdirectory()
    if path:
        entry_widget.delete(0, "end")
        entry_widget.insert(0, path)

def browse_file(entry_widget):
    path = filedialog.askopenfilename()
    if path:
        entry_widget.delete(0, "end")
        entry_widget.insert(0, path)

# ----------------------- GUI -----------------------
def main():
    cfg = load_cfg()

    root = tb.Window(themename="flatly")
    root.title(f"{APP_NAME} — {APP_AUTHOR}")
    root.geometry("960x860")
    root.minsize(880, 760)

    # Menu
    menubar = tk.Menu(root)
    helpmenu = tk.Menu(menubar, tearoff=0)
    helpmenu.add_command(label="About", command=lambda: messagebox.showinfo("About", ABOUT_TEXT))
    helpmenu.add_command(label="Copyright", command=lambda: messagebox.showinfo("Copyright", APP_COPYRIGHT))
    helpmenu.add_separator()
    helpmenu.add_command(label="Exit", command=root.destroy)
    menubar.add_cascade(label="Help", menu=helpmenu)
    root.config(menu=menubar)

    # URL row
    frm_url = ttk.Frame(root, padding=10)
    frm_url.pack(fill="x")
    ttk.Label(frm_url, text="Video / Playlist / Channel URL:").grid(row=0, column=0, sticky="w", columnspan=2)
    url_var = tk.StringVar()
    url_entry = ttk.Entry(frm_url, textvariable=url_var)
    url_entry.grid(row=1, column=0, sticky="we", padx=(0,8))
    top_download_btn = ttk.Button(frm_url, text="Download", bootstyle="success")
    top_download_btn.grid(row=1, column=1, sticky="e")
    frm_url.columnconfigure(0, weight=1)
    url_entry.focus()

    # Mode
    frm_mode = ttk.Frame(root, padding=(10,0))
    frm_mode.pack(fill="x", pady=(8,0))
    ttk.Label(frm_mode, text="Mode:").grid(row=0, column=0, sticky="w")
    mode_var = tk.StringVar(value="Both")
    for i, label in enumerate(("Apple Native (MP4)", "Archival (MKV)", "Both")):
        ttk.Radiobutton(frm_mode, text=label, variable=mode_var, value=label).grid(row=0, column=i+1, padx=8, sticky="w")

    # Output dirs
    frm_out = ttk.Frame(root, padding=(10,5))
    frm_out.pack(fill="x")
    ttk.Label(frm_out, text="Archival output folder (MKV):").grid(row=0, column=0, sticky="w")
    archival_var = tk.StringVar(value=cfg["out_archival"])
    ent_arch = ttk.Entry(frm_out, textvariable=archival_var, width=75); ent_arch.grid(row=0, column=1, sticky="we", padx=6)
    ttk.Button(frm_out, text="Browse…", command=lambda: browse_dir(ent_arch)).grid(row=0, column=2)

    ttk.Label(frm_out, text="iOS output folder (MP4):").grid(row=1, column=0, sticky="w", pady=(6,0))
    ios_var = tk.StringVar(value=cfg["out_ios"])
    ent_ios = ttk.Entry(frm_out, textvariable=ios_var, width=75); ent_ios.grid(row=1, column=1, sticky="we", padx=6, pady=(6,0))
    ttk.Button(frm_out, text="Browse…", command=lambda: browse_dir(ent_ios)).grid(row=1, column=2, pady=(6,0))
    frm_out.columnconfigure(1, weight=1)

    # Advanced
    frm_adv = ttk.LabelFrame(root, text="Advanced (optional)", padding=10)
    frm_adv.pack(fill="x", padx=10, pady=8)

    ttk.Label(frm_adv, text="FFmpeg path:").grid(row=0, column=0, sticky="w")
    ffmpeg_var = tk.StringVar(value=cfg["ffmpeg_path"])
    ent_ff = ttk.Entry(frm_adv, textvariable=ffmpeg_var, width=70); ent_ff.grid(row=0, column=1, sticky="we", padx=6)
    ttk.Button(frm_adv, text="Browse…", command=lambda: browse_file(ent_ff)).grid(row=0, column=2)

    ttk.Label(frm_adv, text="Rate limit (e.g. 4M):").grid(row=1, column=0, sticky="w", pady=(6,0))
    rate_var = tk.StringVar(value=cfg["rate_limit"])
    ttk.Entry(frm_adv, textvariable=rate_var, width=20).grid(row=1, column=1, sticky="w", padx=6, pady=(6,0))

    ttk.Label(frm_adv, text="Proxy (e.g. http://127.0.0.1:8080):").grid(row=2, column=0, sticky="w", pady=(6,0))
    proxy_var = tk.StringVar(value=cfg["proxy"])
    ttk.Entry(frm_adv, textvariable=proxy_var, width=30).grid(row=2, column=1, sticky="w", padx=6, pady=(6,0))

    # Toggles
    playlist_idx_var = tk.BooleanVar(value=cfg["playlist_index"])
    ttk.Checkbutton(frm_adv, text="Include playlist index in filenames", variable=playlist_idx_var).grid(row=3, column=0, columnspan=2, sticky="w", pady=(6,0))

    write_subs_var = tk.BooleanVar(value=cfg["write_subs"])
    embed_subs_var = tk.BooleanVar(value=cfg["embed_subs"])
    ttk.Checkbutton(frm_adv, text="Save subtitles (sidecar .vtt)", variable=write_subs_var).grid(row=4, column=0, sticky="w")
    ttk.Checkbutton(frm_adv, text="Embed subtitles (no sidecar)", variable=embed_subs_var).grid(row=4, column=1, sticky="w")

    write_thumb_var = tk.BooleanVar(value=cfg["write_thumb"])
    embed_thumb_var = tk.BooleanVar(value=cfg["embed_thumb"])
    ttk.Checkbutton(frm_adv, text="Write thumbnail (sidecar)", variable=write_thumb_var).grid(row=5, column=0, sticky="w")
    ttk.Checkbutton(frm_adv, text="Embed thumbnail (no sidecar)", variable=embed_thumb_var).grid(row=5, column=1, sticky="w")

    write_desc_var = tk.BooleanVar(value=cfg["write_desc"])
    write_infojson_var = tk.BooleanVar(value=cfg["write_infojson"])
    ttk.Checkbutton(frm_adv, text="Write description file (.txt)", variable=write_desc_var).grid(row=6, column=0, sticky="w")
    ttk.Checkbutton(frm_adv, text="Write info JSON", variable=write_infojson_var).grid(row=6, column=1, sticky="w")

    sb_mark_var = tk.BooleanVar(value=cfg["sponsorblock_mark"])
    sb_remove_var = tk.BooleanVar(value=cfg["sponsorblock_remove"])
    ttk.Checkbutton(frm_adv, text="SponsorBlock: mark segments", variable=sb_mark_var).grid(row=7, column=0, sticky="w")
    ttk.Checkbutton(frm_adv, text="SponsorBlock: remove segments (cuts)", variable=sb_remove_var).grid(row=7, column=1, sticky="w")

    split_chapters_var = tk.BooleanVar(value=cfg["split_chapters"])
    ttk.Checkbutton(frm_adv, text="Split by chapters (lossless)", variable=split_chapters_var).grid(row=8, column=0, sticky="w", pady=(0,6))

    ttk.Label(frm_adv, text='Subtitle language patterns (comma-separated, e.g. "en.*"):').grid(row=9, column=0, columnspan=3, sticky="w")
    subs_var = tk.StringVar(value=",".join(cfg["subs_langs"]))
    ttk.Entry(frm_adv, textvariable=subs_var).grid(row=10, column=0, columnspan=3, sticky="we", pady=(0,6))

    ttk.Separator(frm_adv).grid(row=11, column=0, columnspan=3, sticky="we", pady=8)
    ttk.Label(frm_adv, text="Speed (optional): aria2c external downloader").grid(row=12, column=0, sticky="w")
    use_aria2c_var = tk.BooleanVar(value=cfg.get("use_aria2c", False))
    ttk.Checkbutton(frm_adv, text="Use aria2c (requires aria2c installed)", variable=use_aria2c_var).grid(row=12, column=1, sticky="w")
    ttk.Label(frm_adv, text="Connections:").grid(row=13, column=0, sticky="e")
    aria2c_conns_var = tk.StringVar(value=str(cfg.get("aria2c_conns", 16)))
    ttk.Entry(frm_adv, textvariable=aria2c_conns_var, width=6).grid(row=13, column=1, sticky="w")
    ttk.Label(frm_adv, text="Chunk size (e.g. 5M):").grid(row=13, column=1, sticky="e", padx=(120,0))
    aria2c_chunk_var = tk.StringVar(value=cfg.get("aria2c_chunk","5M"))
    ttk.Entry(frm_adv, textvariable=aria2c_chunk_var, width=8).grid(row=13, column=1, sticky="w", padx=(240,0))
    frm_adv.columnconfigure(1, weight=1)

    # Progress bars + status
    frm_prog = ttk.Frame(root, padding=(10,0))
    frm_prog.pack(fill="x", pady=(2,0))
    progress = ttk.Progressbar(frm_prog, mode="determinate", maximum=100)
    progress.pack(fill="x")
    status_lbl = ttk.Label(frm_prog, text="Idle.")
    status_lbl.pack(anchor="w", pady=(4,0))

    frm_overall = ttk.Frame(root, padding=(10,4))
    frm_overall.pack(fill="x")
    overall_bar = ttk.Progressbar(frm_overall, mode="determinate", maximum=100)
    overall_bar.pack(fill="x")
    overall_lbl = ttk.Label(frm_overall, text="Waiting…")
    overall_lbl.pack(anchor="w", pady=(4,0))

    # Log
    log = tk.Text(root, height=12, wrap="word")
    log.pack(fill="both", expand=True, padx=10, pady=8)

    # Bottom buttons
    frm_btn = ttk.Frame(root, padding=10)
    frm_btn.pack(fill="x")
    btn = ttk.Button(frm_btn, text="Download", bootstyle="success")
    btn.pack(side="left")
    ttk.Button(frm_btn, text="Exit", command=root.destroy).pack(side="right")

    # Start action
    def start_download():
        cfg["out_archival"] = archival_var.get().strip()
        cfg["out_ios"] = ios_var.get().strip()
        cfg["ffmpeg_path"] = ffmpeg_var.get().strip()
        cfg["rate_limit"] = rate_var.get().strip()
        cfg["proxy"] = proxy_var.get().strip()
        cfg["playlist_index"] = bool(playlist_idx_var.get())

        cfg["write_subs"] = bool(write_subs_var.get())
        cfg["embed_subs"] = bool(embed_subs_var.get())
        cfg["subs_langs"] = [s.strip() for s in subs_var.get().split(",") if s.strip()]

        cfg["write_thumb"] = bool(write_thumb_var.get())
        cfg["embed_thumb"] = bool(embed_thumb_var.get())

        cfg["write_desc"] = bool(write_desc_var.get())
        cfg["write_infojson"] = bool(write_infojson_var.get())
        cfg["sponsorblock_mark"] = bool(sb_mark_var.get())
        cfg["sponsorblock_remove"] = bool(sb_remove_var.get())
        cfg["split_chapters"] = bool(split_chapters_var.get())

        cfg["use_aria2c"] = bool(use_aria2c_var.get())
        cfg["aria2c_conns"] = int(aria2c_conns_var.get() or 16)
        cfg["aria2c_chunk"] = aria2c_chunk_var.get().strip() or "5M"

        save_cfg(cfg)

        url = url_var.get().strip()
        mode = mode_var.get()
        run_download(url, mode, cfg, log, btn, progress, status_lbl, overall_bar, overall_lbl)

    top_download_btn.configure(command=start_download)
    btn.configure(command=start_download)
    root.bind("<Control-Return>", lambda e: start_download())
    url_entry.focus()

    root.mainloop()

if __name__ == "__main__":
    main()
