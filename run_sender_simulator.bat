@echo off
echo Checking virtual environment presence
IF NOT EXIST env\Scripts\python.exe (
    echo Plesae create virtual environment
    echo use install_dependencies.bat
    exit /b 2
) ELSE (
    echo Using virtual env: env
)

env\Scripts\python.exe sender_simulator\sender_simulator.py