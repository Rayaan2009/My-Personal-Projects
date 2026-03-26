from pathlib import Path
import shutil

import yt_dlp
from yt_dlp.utils import DownloadError


DEFAULT_DOWNLOAD_DIR = Path.home() / "Downloads" / "YouTube"
QUALITY_PRESETS = {
    "1": ("Best available (up to 8K if available)", 4320),
    "2": ("4K or lower", 2160),
    "3": ("1080p or lower", 1080),
    "4": ("720p or lower", 720),
    "5": ("480p or lower", 480),
    "6": ("Audio only (mp3)", None),
}


def prompt_url():
    while True:
        url = input("Paste the video link here: ").strip()
        if url:
            return url
        print("Please enter a video URL.")


def prompt_quality():
    print("\nChoose quality:")
    for key, (label, _) in QUALITY_PRESETS.items():
        print(f"{key}. {label}")

    choice = input("Enter 1-6 [1]: ").strip() or "1"
    if choice not in QUALITY_PRESETS:
        print("Invalid choice. Using 1.")
        choice = "1"
    return choice


def prompt_output_dir():
    raw_value = input(f"Save folder [{DEFAULT_DOWNLOAD_DIR}]: ").strip()
    output_dir = Path(raw_value).expanduser() if raw_value else DEFAULT_DOWNLOAD_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def build_base_options(output_dir):
    options = {
        "outtmpl": str(output_dir / "%(title)s.%(ext)s"),
        "restrictfilenames": False,
        "noplaylist": True,
    }

    node_path = shutil.which("node")
    if node_path:
        options["js_runtimes"] = {"node": {"path": node_path}}

    return options


def build_attempts(choice):
    if choice == "6":
        return [
            {
                "label": "best audio",
                "options": {
                    "format": "bestaudio/best",
                    "postprocessors": [
                        {
                            "key": "FFmpegExtractAudio",
                            "preferredcodec": "mp3",
                            "preferredquality": "192",
                        }
                    ],
                },
            }
        ]

    _, max_height = QUALITY_PRESETS[choice]
    return [
        {
            "label": f"separate video+audio up to {max_height}p",
            "options": {
                "format": (
                    f"bestvideo[height<={max_height}]+bestaudio"
                    f"/bestvideo+bestaudio"
                ),
                "merge_output_format": "mkv",
            },
        },
        {
            "label": f"combined stream up to {max_height}p",
            "options": {
                "format": f"best[height<={max_height}]/best",
            },
        },
    ]


def download_with_fallback(url, output_dir, choice):
    base_options = build_base_options(output_dir)
    attempts = build_attempts(choice)
    last_error = None

    for index, attempt in enumerate(attempts, start=1):
        options = {**base_options, **attempt["options"]}
        print(f"\nAttempt {index}/{len(attempts)}: {attempt['label']}")
        try:
            with yt_dlp.YoutubeDL(options) as downloader:
                downloader.download([url])
            return
        except DownloadError as error:
            last_error = error
            message = str(error)
            if "HTTP Error 403" in message and index < len(attempts):
                print("YouTube blocked that stream. Retrying with a safer format...")
                continue
            raise

    if last_error:
        raise last_error


def main():
    try:
        url = prompt_url()
        choice = prompt_quality()
        output_dir = prompt_output_dir()
        quality_label, _ = QUALITY_PRESETS[choice]

        print(f"\nSaving to: {output_dir}")
        print(f"Quality preset: {quality_label}")
        print("Starting download... sit tight!")
        download_with_fallback(url, output_dir, choice)
        print("Download finished!")
    except KeyboardInterrupt:
        print("\nDownload cancelled.")
    except DownloadError as error:
        print(f"\nDownload failed: {error}")


if __name__ == "__main__":
    main()