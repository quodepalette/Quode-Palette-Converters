# Quode Palette Video Converter

Convert common video formats with FFmpeg from the command line or the included Windows launcher.

## Formats

MP4, MKV, WebM, MOV, AVI and GIF output. Input files must be readable by your FFmpeg build.

## Requirements

- Python 3.10 or newer
- FFmpeg: bundled in the collection's shared `ffmpeg/bin` folder (used automatically by the launcher), or placed at `ffmpeg\bin\ffmpeg.exe` beside the launcher, or available on PATH. If none is found, the launcher offers to download it automatically (about 200 MB, one time)

## Windows

Double-click `Quode-Palette-Video-Converter.bat`, enter or drag a file path into the prompt, then select the output format.

## Command line

```bash
python -m pip install .
quode-video clip.mov --to mp4
quode-video ./videos --to webm --recursive --output-dir ./converted
```

Existing outputs are skipped unless `--overwrite` is supplied. The converter reports errors and continues with other files. Video conversion may take time and can reduce quality depending on the selected format and settings. GIF output has no audio and is resized to a maximum width of 640 pixels.

## License

MIT. See `LICENSE`.

## Progress display

While converting, the tool shows a live progress bar for each file with percent complete, processed/total time and an estimated time remaining, plus a "File 1 of N" header for folders. If FFmpeg can't report a duration, a working indicator with elapsed time is shown instead. Press Ctrl+C to cancel; the partial output file is removed.
