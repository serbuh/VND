@echo off

:check_virtualenv
echo Checking virtual environment presence
IF NOT EXIST env\Scripts\python.exe (
    echo Plesae create virtual environment
    GOTO if_to_install_virtualenv
) ELSE (
    echo Using virtual env: env
    GOTO install_wheels
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

:install_wheels
echo Installing wheels ...
for %%x in (downloaded_req/*.whl) do env\Scripts\python -m pip install --retries 0 downloaded_req\\"%%x"
echo Finished. Check if no errors. Otherwise run this script again until errors disapear