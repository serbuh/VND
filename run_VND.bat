@echo off
rem echo Checking virtual environment presence
IF NOT EXIST env\Scripts\python.exe (
    echo Plesae create virtual environment
    echo use install_dependencies.bat
    exit /b 2
) ELSE (
    echo Using virtual env: env
)

rem Get version
FOR /F "tokens=*" %%g IN ('type deploy\version.txt') do (SET ver=%%g)
echo VND v%ver%

env\Scripts\python.exe -m telemetry_server.server