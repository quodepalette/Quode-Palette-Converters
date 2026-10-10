@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title Quode Palette Image Converter

:welcome
cls
echo   /$$$$$$                            /$$                 /$$$$$$$           /$$             /$$     /$$
echo  /$$__  $$                          ^| $$                ^| $$__  $$         ^| $$            ^| $$    ^| $$
echo ^| $$  \ $$ /$$   /$$  /$$$$$$   /$$$$$$$  /$$$$$$       ^| $$  \ $$ /$$$$$$ ^| $$  /$$$$$$  /$$$$$$ /$$$$$$    /$$$$$$
echo ^| $$  ^| $$^| $$  ^| $$ /$$__  $$ /$$__  $$ /$$__  $$      ^| $$$$$$$/^|____  $$^| $$ /$$__  $$^|_  $$_/^|_  $$_/   /$$__  $$
echo ^| $$  ^| $$^| $$  ^| $$^| $$  \ $$^| $$  ^| $$^| $$$$$$$$      ^| $$____/  /$$$$$$$^| $$^| $$$$$$$$  ^| $$    ^| $$    ^| $$$$$$$$
echo ^| $$/$$ $$^| $$  ^| $$^| $$  ^| $$^| $$  ^| $$^| $$_____/      ^| $$      /$$__  $$^| $$^| $$_____/  ^| $$ /$$^| $$ /$$^| $$_____/
echo ^|  $$$$$$/^|  $$$$$$/^|  $$$$$$/^|  $$$$$$$^|  $$$$$$$      ^| $$     ^|  $$$$$$$^| $$^|  $$$$$$$  ^|  $$$$/^|  $$$$/^|  $$$$$$$
echo.  \____ $$$ \______/  \______/  \_______/ \_______/      ^|__/      \_______/^|__/ \_______/   \___/   \___/   \_______/
echo.      \__/
echo. 
echo.
echo.              QUODE PALETTE IMAGE CONVERTER
echo.   ======================================================
echo.  Convert images to the format you need.
echo   Targets: PNG, JPG, WEBP, BMP, TIFF, GIF, ICO
echo.
where py >nul 2>nul
if errorlevel 1 (
    where python >nul 2>nul
    if errorlevel 1 (
        echo ERROR: Python was not found on this computer.
        echo Install Python 3.10 or newer, then run this file again.
        echo Download: https://www.python.org/downloads/windows/
        echo.
        pause
        exit /b 2
    )
    set "PYTHON_CMD=python"
) else (
    set "PYTHON_CMD=py -3"
)

%PYTHON_CMD% -c "import PIL" >nul 2>nul
if errorlevel 1 (
    echo Pillow is not installed. Installing the required image library...
    %PYTHON_CMD% -m pip install --user "Pillow>=10.4.0"
    if errorlevel 1 (
        echo.
        echo ERROR: Pillow could not be installed.
        echo Check your internet connection and Python pip installation.
        pause
        exit /b 2
    )
)

echo Step 1: Drag an image file or folder into this window,
echo         or type its full path, then press Enter.
set "INPUT_PATH="
set /p "INPUT_PATH=Input path: "
if not defined INPUT_PATH goto empty_input
set "INPUT_PATH=%INPUT_PATH:"=%"
if not exist "%INPUT_PATH%" (
    echo.
    echo ERROR: That path does not exist.
    pause
    goto welcome
)

echo.
echo Step 2: Choose the output format.
echo   1. PNG
echo   2. JPG
echo   3. WEBP
echo   4. BMP
echo   5. TIFF
echo   6. GIF
echo   7. ICO
set "CHOICE="
set /p "CHOICE=Format number: "
set "FORMAT="
if "%CHOICE%"=="1" set "FORMAT=png"
if "%CHOICE%"=="2" set "FORMAT=jpg"
if "%CHOICE%"=="3" set "FORMAT=webp"
if "%CHOICE%"=="4" set "FORMAT=bmp"
if "%CHOICE%"=="5" set "FORMAT=tiff"
if "%CHOICE%"=="6" set "FORMAT=gif"
if "%CHOICE%"=="7" set "FORMAT=ico"
if not defined FORMAT (
    echo.
    echo Please choose a number from 1 to 7.
    pause
    goto welcome
)

echo.
echo Include files in subfolders too?
set "RECURSIVE="
set /p "RECURSIVE=Type Y for yes, or press Enter for no: "
set "RECURSIVE_FLAG="
if /i "%RECURSIVE%"=="Y" set "RECURSIVE_FLAG=--recursive"

echo.
echo Existing output files will be kept. Nothing will be overwritten.
echo Starting conversion...
echo.
%PYTHON_CMD% -m quode_palette_image_converter "%INPUT_PATH%" --to %FORMAT% %RECURSIVE_FLAG%
set "RESULT=%ERRORLEVEL%"
echo.
if "%RESULT%"=="0" (
    echo Conversion finished.
) else (
    echo The conversion finished with an error. Read the message above for details.
)
echo.
pause
exit /b %RESULT%

:empty_input
echo Please enter a file or folder path.
pause
goto welcome
