@echo off
rem echo Checking virtual environment presence
IF NOT EXIST env\Scripts\python.exe (
    echo Plesae create virtual environment
    echo use install_dependencies.bat
    exit /b 2
) ELSE (
    echo Using virtual env: env
)

env\Scripts\python.exe emulator\data_sender.py