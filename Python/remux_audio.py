#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

# --- CONFIG ---
# In your case:
#  *_1.mkv = DV source (take audio from here)
#  *_2.mkv = AV1 IMAX source (take video from here)
DV_SUFFIX = "_1.mkv"
AV1_SUFFIX = "_2.mkv"

# Set to True if you want to keep subtitles from the AV1 file too
KEEP_SUBS_FROM_AV1 = True

# Choose output naming
OUTPUT_SUFFIX = "_AV1_video_DV_audio.mkv"


def run(cmd: list[str]) -> None:
    print("\nRunning:\n", " ".join(cmd), "\n")
    subprocess.run(cmd, check=True)


def main() -> None:
    folder = Path.cwd()

    # Find matching pairs like Spider-Man_No_Way-Home_1.mkv and _2.mkv
    dv_files = sorted(folder.glob(f"*{DV_SUFFIX}"))

    if not dv_files:
        raise SystemExit(f"No files ending with {DV_SUFFIX} found in: {folder}")

    for dv_path in dv_files:
        base = dv_path.name[: -len(DV_SUFFIX)]
        av1_path = folder / f"{base}{AV1_SUFFIX}"

        if not av1_path.exists():
            print(f"Skipping (no AV1 pair found): {av1_path.name}")
            continue

        out_path = folder / f"{base}{OUTPUT_SUFFIX}"

        # Build ffmpeg command:
        # Input 0 = AV1 file -> take VIDEO from here
        # Input 1 = DV file  -> take AUDIO from here
        cmd = [
            "ffmpeg",
            "-hide_banner",
            "-y",
            "-i", str(av1_path),
            "-i", str(dv_path),

            # Map video from AV1 (input 0)
            "-map", "0:v:0",

            # Map the "best" audio from DV (input 1)
            # If DV has multiple audios, you can change to 1:a:0 or 1:a:m:language:eng etc.
            "-map", "1:a:0",
        ]

        if KEEP_SUBS_FROM_AV1:
            # Map all subtitles from AV1 if present (won't error if none due to '?')
            cmd += ["-map", "0:s?"]

        # Copy streams without re-encoding (fast, lossless)
        cmd += [
            "-c", "copy",

            # Useful metadata (optional)
            "-metadata", "title=Spider-Man: No Way Home (AV1 video + DV audio)",

            str(out_path)
        ]

        run(cmd)

        print(f"✅ Created: {out_path.name}")


if __name__ == "__main__":
    main()