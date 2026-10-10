@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title Quode Palette Audio Converter
mode con: cols=125 lines=45

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
echo.              QUODE PALETTE AUDIO CONVERTER
echo.   ======================================================
echo.   Convert audio files to the format you need.
echo   Targets: MP3, M4A, WAV, FLAC, OGG, OPUS, AAC, WMA
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

rem --- Locate FFmpeg: bundled copy first, then PATH ---
set "FFMPEG_PATH="
if exist "%~dp0ffmpeg\bin\ffmpeg.exe" set "FFMPEG_PATH=%~dp0ffmpeg\bin\ffmpeg.exe"
if not defined FFMPEG_PATH if exist "%~dp0..\ffmpeg\bin\ffmpeg.exe" for %%I in ("%~dp0..\ffmpeg\bin\ffmpeg.exe") do set "FFMPEG_PATH=%%~fI"
if not defined FFMPEG_PATH where ffmpeg >nul 2>nul && set "FFMPEG_PATH=ffmpeg"
if not defined FFMPEG_PATH goto no_ffmpeg
:ffmpeg_ready
echo Step 1: Drag an audio file or folder into this window,
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
echo   1. MP3
echo   2. M4A
echo   3. WAV
echo   4. FLAC
echo   5. OGG
echo   6. OPUS
echo   7. AAC
echo   8. WMA
set "CHOICE="
set /p "CHOICE=Format number: "
set "FORMAT="
if "%CHOICE%"=="1" set "FORMAT=mp3"
if "%CHOICE%"=="2" set "FORMAT=m4a"
if "%CHOICE%"=="3" set "FORMAT=wav"
if "%CHOICE%"=="4" set "FORMAT=flac"
if "%CHOICE%"=="5" set "FORMAT=ogg"
if "%CHOICE%"=="6" set "FORMAT=opus"
if "%CHOICE%"=="7" set "FORMAT=aac"
if "%CHOICE%"=="8" set "FORMAT=wma"
if not defined FORMAT (
echo.
    echo Please choose a number from 1 to 8.
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
echo Existing output files will be kept. The converter will not overwrite them.
echo Starting conversion...
echo.
if "%FFMPEG_PATH%"=="ffmpeg" (
    %PYTHON_CMD% -m quode_palette_audio_converter "%INPUT_PATH%" --to %FORMAT% %RECURSIVE_FLAG%
) else (
    %PYTHON_CMD% -m quode_palette_audio_converter "%INPUT_PATH%" --to %FORMAT% %RECURSIVE_FLAG% --ffmpeg "%FFMPEG_PATH%"
)
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

:no_ffmpeg
cls
echo.
echo   FFmpeg was not found on this computer.
echo   FFmpeg is the engine that does the actual converting.
echo.
echo   I can download it for you now:
echo     - Size:    about 200 MB, one time only
echo     - Source:  https://github.com/BtbN/FFmpeg-Builds
echo     - Needs an internet connection
echo.
set "FF_DL="
set /p "FF_DL=Download FFmpeg now? Type Y for yes, or press Enter to cancel: "
if /i not "%FF_DL%"=="Y" goto ffmpeg_cancel

rem Use the shared folder when this tool sits inside the converters collection,
rem otherwise keep FFmpeg beside this launcher.
set "FF_DIR=%~dp0ffmpeg\bin"
if exist "%~dp0..\ffmpeg\README.txt" set "FF_DIR=%~dp0..\ffmpeg\bin"
for %%I in ("%FF_DIR%") do set "FF_DIR=%%~fI"
set "FF_DEST=%FF_DIR%\ffmpeg.exe"
for %%I in ("%FF_DIR%\..\LICENSE.txt") do set "FF_LIC=%%~fI"
set "FF_URL=https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
set "FF_ZIP=%TEMP%\quode-ffmpeg-download.zip"
if not exist "%FF_DIR%" mkdir "%FF_DIR%"
if not exist "%FF_DIR%" goto ffmpeg_failed

echo.
echo   Downloading FFmpeg. Please keep this window open...
echo.
where curl.exe >nul 2>nul
if errorlevel 1 goto ff_ps_download
curl.exe -L --fail --progress-bar -o "%FF_ZIP%" "%FF_URL%"
if errorlevel 1 goto ffmpeg_failed
goto ff_extract

:ff_ps_download
echo   Downloading... this can take a few minutes.
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ProgressPreference='SilentlyContinue'; [Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -UseBasicParsing -Uri $env:FF_URL -OutFile $env:FF_ZIP"
if errorlevel 1 goto ffmpeg_failed

:ff_extract
echo.
echo   Download complete. Extracting FFmpeg...
powershell -NoProfile -ExecutionPolicy Bypass -Command "Add-Type -AssemblyName System.IO.Compression.FileSystem; $zip=[IO.Compression.ZipFile]::OpenRead($env:FF_ZIP); try { $exe=$zip.Entries | Where-Object { $_.FullName -like '*/bin/ffmpeg.exe' } | Select-Object -First 1; if(-not $exe){ exit 3 }; [IO.Compression.ZipFileExtensions]::ExtractToFile($exe,$env:FF_DEST,$true); $lic=$zip.Entries | Where-Object { $_.FullName -like '*/LICENSE.txt' } | Select-Object -First 1; if($lic){ [IO.Compression.ZipFileExtensions]::ExtractToFile($lic,$env:FF_LIC,$true) } } finally { $zip.Dispose() }"
if errorlevel 1 goto ffmpeg_failed
del "%FF_ZIP%" >nul 2>nul
if not exist "%FF_DEST%" goto ffmpeg_failed
"%FF_DEST%" -version >nul 2>nul
if errorlevel 1 goto ffmpeg_failed

set "FFMPEG_PATH=%FF_DEST%"
echo.
echo   FFmpeg is installed and ready.
ping -n 3 127.0.0.1 >nul
goto ffmpeg_ready

:ffmpeg_failed
del "%FF_ZIP%" >nul 2>nul
echo.
echo   ERROR: FFmpeg could not be downloaded or installed.
echo   Check your internet connection and try again, or install FFmpeg yourself
echo   and add it to PATH. Download page: https://github.com/BtbN/FFmpeg-Builds/releases
echo.
pause
exit /b 2

:ffmpeg_cancel
echo.
echo   FFmpeg is required for this converter. Nothing was downloaded.
echo.
pause
exit /b 2
