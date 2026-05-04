@echo off
:: PokemonStadiumRecomp setup - Windows
::
:: What this does:
::   1. Clones N64Recomp into n64recomp\ at the SHA pinned in
::      n64recomp.pin (or junctions to a sister checkout if present).
::   2. Initializes the disasm submodule (pret/pokestadium).
::   3. Stages the verified baserom.z64 into disasm\baseroms\us\.
::   4. (Optional) Clones Ares emulator if WITH_ARES=1.

setlocal enabledelayedexpansion

set "N64RECOMP_REPO=https://github.com/N64Recomp/N64Recomp.git"
set "ARES_REPO=https://github.com/ares-emulator/ares.git"
set "SISTER_N64RECOMP=..\N64Recomp"

:: ---- Parse SHA from n64recomp.pin ----
set "SHA="
for /f "usebackq tokens=1,* delims==" %%a in ("n64recomp.pin") do (
    set "key=%%a"
    set "key=!key: =!"
    if "!key!"=="sha" (
        set "SHA=%%b"
        set "SHA=!SHA: =!"
    )
)
if not defined SHA (
    echo Error: no sha found in n64recomp.pin
    exit /b 1
)

:: ---- Provision n64recomp\ ----
if not exist "n64recomp" (
    if exist "%SISTER_N64RECOMP%\.git" (
        echo Junctioning n64recomp -^> %SISTER_N64RECOMP%
        mklink /J n64recomp %SISTER_N64RECOMP%
    ) else (
        echo Cloning N64Recomp...
        git clone --recurse-submodules %N64RECOMP_REPO% n64recomp
    )
)

:: ---- Pin enforcement ----
for /f %%h in ('git -C n64recomp rev-parse HEAD') do set "ACTUAL=%%h"
if not "!ACTUAL!"=="%SHA%" (
    echo Note: n64recomp HEAD ^(!ACTUAL!^) != pinned ^(%SHA%^).
    echo   To align: git -C n64recomp checkout %SHA%
    echo   To roll forward: edit n64recomp.pin to sha = !ACTUAL!
)

:: ---- Disasm submodule ----
git submodule update --init --recursive disasm

:: ---- Stage ROM into disasm ----
if exist "baserom.z64" (
    if not exist "disasm\baseroms\us\baserom.z64" (
        if not exist "disasm\baseroms\us" mkdir "disasm\baseroms\us"
        copy /Y "baserom.z64" "disasm\baseroms\us\baserom.z64" >nul
        echo Staged baserom.z64 -^> disasm\baseroms\us\
    )
)

:: ---- Build aspmain_combined.bin from the user's ROM ----
:: RSPRecomp needs rspboot+aspMain as one contiguous binary. The script
:: extracts bytes from baserom.z64 (hash-checked) and writes
:: aspmain_combined.bin at the project root. ROM-derived bytes are never
:: committed; this regenerates them from the user's own ROM.
if exist "baserom.z64" (
    if not exist "aspmain_combined.bin" (
        where python >nul 2>nul
        if not errorlevel 1 (
            python tools\build_aspmain_combined.py
        ) else (
            echo WARNING: python not found; run tools\build_aspmain_combined.py manually before configuring CMake
        )
    )
)

:: ---- Ares oracle (optional, opt-in) ----
if "%WITH_ARES%"=="1" (
    if not exist "ares-emulator\.git" (
        echo Cloning Ares ^(this is a large repo^)...
        git clone %ARES_REPO% ares-emulator
    )
)

echo.
echo Setup complete.
echo Next:
echo   1. cd disasm ^&^& make init ^&^& make
echo   2. (back at root) cmake -S . -B build -G "Visual Studio 17 2022" -A x64

endlocal
