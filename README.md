# Parallel Youtube Titles to MP3

Download audio from YouTube by searching with human-readable titles, then convert the best audio stream to MP3 with metadata and thumbnails.

This repo originally shipped as a Python 2 + `youtube-dl` + Google Data API script. That version is not viable anymore:

- it does not parse on Python 3
- it hardcodes personal file paths
- it requires a Google API key for a task that `yt-dlp` can already handle
- the dependency stack is stale enough to break on a current machine

The current version replaces that with a Python 3 implementation built on `yt-dlp`.

## What It Does

- reads a newline-delimited titles file such as [titles.txt](./titles.txt)
- searches YouTube for the first result matching each title
- downloads the best available audio
- converts the result to MP3
- embeds metadata and thumbnails
- records successful video IDs in a download archive
- writes failed titles to an errors file

There are two entry points:

- [list2mp3_seq.py](./list2mp3_seq.py) for sequential execution
- [list2mp3_mp.py](./list2mp3_mp.py) for parallel execution

## Requirements

- Python 3.10+
- `ffmpeg` available on `PATH`

Install Python dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Install FFmpeg if needed:

```bash
sudo apt update
sudo apt install -y ffmpeg
```

## Usage

Sequential:

```bash
python3 list2mp3_seq.py \
  --titles-file titles.txt \
  --download-dir downloads
```

Parallel:

```bash
python3 list2mp3_mp.py \
  --titles-file titles.txt \
  --download-dir downloads \
  --jobs 8
```

Dry run to resolve matches without downloading:

```bash
python3 list2mp3_mp.py --dry-run
```

### Options

Both entry points support:

- `--titles-file`
- `--download-dir`
- `--errors-file`
- `--archive-file`
- `--dry-run`

The parallel version also accepts:

- `--jobs`

## Why The Parallel Version Changed

The original "multiprocess" version was not actually production-grade parallel download code. It relied on:

- a global YouTube API client
- stale Python 2 exception handling
- a shared archive file without safe coordination

The current implementation uses a worker pool while coordinating duplicate video IDs in-memory for the current run. That avoids multiple workers downloading the same resolved video at once and appends archive entries only after successful downloads.

## Titles File

Use one query per line:

```text
Ed Sheeran - Happier [Official Audio]
Daft Punk - Something About Us
Radiohead - No Surprises
```

More specific titles usually produce better first-result matches.

## Output Files

By default the scripts use:

- `titles.txt`
- `downloads/`
- `errors.txt`
- `archive.txt`

`archive.txt` stores entries in a `yt-dlp`-compatible style:

```text
youtube 8TpcBDJZsJA
```

## Helper Script

[dir2list.py](./dir2list.py) scans directories non-recursively and converts local video filenames into a titles file:

```bash
python3 dir2list.py ~/Videos ~/MoreVideos --output titles.txt
```

## Legal Note

Downloading copyrighted content may violate the law, platform rules, or license terms depending on your jurisdiction and the content involved. Use the tool only where you have the right to access, download, and convert the media.
