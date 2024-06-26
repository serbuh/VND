@echo off

:check_virtualenv
rem echo Checking virtual environment presence
IF NOT EXIST env\Scripts\python.exe (
    echo Plesae create virtual environment
    GOTO if_to_install_virtualenv
) ELSE (
    echo Using virtual env: env
    GOTO install_reqs
)

:if_to_install_virtualenv
echo Your python version:
python --version
set /p choice=Run "python -m venv env" [Y/n]?
if '%choice%'=='Y' GOTO install_virtualenv
if '%choice%'=='y' GOTO install_virtualenv
if '%choice%'=='' GOTO install_virtualenv
if '%choice%'=='N' exit /b 2
if '%choice%'=='n' exit /b 2
echo Unrecognized choice %choice%
GOTO if_to_install_virtualenv

:install_virtualenv
python -m venv env
GOTO check_virtualenv

:install_reqs
echo Installing requirements ...
env\Scripts\python -m pip install --upgrade pip
env\Scripts\python -m pip install -r requirements.txt
echo Finished.
pause