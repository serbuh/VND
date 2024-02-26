@ECHO OFF

set /p Version=<../deploy/version.txt
echo Preparing version %Version%

:start
Echo [1] VND
ECHO [2] Prepare pip requirements
SET /p choice=
IF NOT '%choice%'=='' SET choice=%choice:~0,1%
IF '%choice%'=='1' GOTO prepare_VND
IF '%choice%'=='2' GOTO prepare_pip_requirements
ECHO "%choice%" is not valid
ECHO.
GOTO start

:prepare_pip_requirements
set req_folder=..\downloaded_req
echo remove all previous wheels
del /q "%req_folder%\*.*"
echo Downloading wheels
pip download -r ..\requirements.txt -d %req_folder%
exit \b 2

:prepare_VND
cd ..
echo Packing VND_v%Version%.zip
7z a -tzip ..\VND_v%Version%.zip -xr!env -xr!.git -xr!.gitignore -xr!.gitmodules ..\VND
rem 7z a -sfx7z.sfx ..\VND_v%Version%.exe -xr!.git -xr!deploy.bat -xr!env ..\VND
exit \b 2