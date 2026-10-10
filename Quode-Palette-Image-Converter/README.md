# Quode Palette Image Converter

A straightforward image converter for Windows and the command line. Convert one image or process a folder with a few commands.

## Features

- Convert to PNG, JPG, WebP, BMP, TIFF, GIF or ICO.
- Convert one file or a folder of images, with optional subfolder scanning.
- Keep existing output files by default.
- Apply EXIF orientation automatically.
- Handle transparent images when saving as JPG by placing them on a white background.
- Continue through a batch when an individual file cannot be converted.
- Includes a Windows `.bat` launcher with a Quode Palette welcome screen.

## Requirements

- Python 3.10 or newer
- Pillow, which the Windows launcher installs for your user account if it is missing

The first launch may need an internet connection to install Pillow. Python must already be installed.

## Windows use

1. Extract the ZIP file.
2. Double-click `Quode-Palette-Image-Converter.bat`.
3. Follow the prompts and choose the format you want.

You can drag a file or folder into the command window when it asks for an input path.

## Install from source

```bash
git clone https://github.com/YOUR-USERNAME/quode-palette-image-converter.git
cd quode-palette-image-converter
python -m pip install .
```

Replace `YOUR-USERNAME` with the GitHub account that hosts the repository.

## Usage

Convert WebP to JPG:

```bash
quode-image photo.webp --to jpg
```

Convert a folder to PNG:

```bash
quode-image ./photos --to png
```

Include subfolders and save results elsewhere:

```bash
quode-image ./photos --to webp --recursive --output-dir ./converted
```

Set JPEG or WebP quality from 1 to 100:

```bash
quode-image photo.png --to webp --quality 85
```

Replace existing output files:

```bash
quode-image photo.png --to jpg --overwrite
```

Run `quode-image --help` for all options. From the project directory, you can also use `python -m quode_palette_image_converter`.

## Notes

- Animated images are converted from their first frame. The output is a still image, including when the target is GIF.
- JPG does not support transparency. Transparent areas are filled with white.
- Image support depends on the installed Pillow build. A file extension alone does not guarantee that its contents can be decoded.
- Converting to a lossy format such as JPG or WebP may reduce image quality.

## Development

Run the tests with:

```bash
python -m unittest discover -s tests -v
```

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
