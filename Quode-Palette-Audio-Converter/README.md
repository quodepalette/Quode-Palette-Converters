# Quode Palette Audio Converter

A command-line tool for converting audio files with FFmpeg. Convert one file or process a folder, with clear results and safe defaults.

## Features

- Convert common formats, including WAV, MP3, M4A, FLAC, OGG, Opus, AAC and WMA.
- Process a folder, with optional subfolder scanning.
- Keep existing outputs by default. Use `--overwrite` to replace them.
- Choose MP3 quality and provide a custom FFmpeg path.
- Report failed conversions and continue with the remaining files.

## Windows use

1. Extract the ZIP file.
2. Double-click `Quode-Palette-Audio-Converter.bat`.
3. Follow the prompts to choose an audio file or folder and an output format.

The Windows launcher uses the FFmpeg bundled in the shared `ffmpeg/bin` folder of the Quode Palette Converters collection, and falls back to FFmpeg on your `PATH`. Python must be installed.

## Requirements

- Python 3.10 or newer
- FFmpeg: bundled with the Windows launcher in the collection's `ffmpeg/bin` folder, or installed and available on your `PATH`. If FFmpeg is missing, the Windows launcher offers to download it for you the first time you run it

Check FFmpeg with `ffmpeg -version`. The converter does not download executables automatically. Install FFmpeg from its official project or a trusted package manager.

## Windows quick launcher

Windows users can double-click `Quode-Palette-Audio-Converter.bat` for a guided command-line experience. Drag an audio file or folder into the window, choose the target format, and decide whether to include subfolders. Existing output files are kept by default.

The launcher requires Python 3.10 or newer and FFmpeg. It checks for both (the bundled FFmpeg counts) and displays an error if either is missing. It does not download or install software without your permission. See the requirements above if setup is needed.

## Install from source

```bash
git clone https://github.com/YOUR-USERNAME/quode-palette-audio-converter.git
cd quode-palette-audio-converter
python -m pip install .
```

Replace `YOUR-USERNAME` with the GitHub account hosting the repository.

## Usage

Convert M4A to MP3:

```bash
quode-audio recording.m4a --to mp3
```

Convert WAV to FLAC:

```bash
quode-audio recording.wav --to flac
```

Convert every supported audio file in a folder:

```bash
quode-audio ./audio --to mp3
```

Include subfolders and write results to another folder:

```bash
quode-audio ./audio --to mp3 --recursive --output-dir ./converted
```

Replace an existing output:

```bash
quode-audio recording.m4a --to mp3 --overwrite
```

Use a custom FFmpeg executable:

```bash
quode-audio recording.m4a --to mp3 --ffmpeg "C:\Tools\ffmpeg\bin\ffmpeg.exe"
```

For MP3, quality ranges from `0` (higher quality, usually larger files) to `9` (lower quality, usually smaller files). The default is `2`.

```bash
quode-audio recording.wav --to mp3 --quality 2
```

Run `quode-audio --help` for all options. You can also run `python -m quode_palette_audio_converter` from the project directory without installing the package.

## Notes

- The first audio stream is converted. Video and other non-audio streams are not copied.
- File extensions are checked before conversion, but FFmpeg must still be able to read the actual file contents.
- Converting a lossy format to WAV does not restore information that was already lost.
- Available codecs depend on the FFmpeg build. Missing codecs are reported as conversion errors.

## Development

Run the tests with:

```bash
python -m unittest discover -s tests -v
```

## License

MIT. See [LICENSE](LICENSE).
