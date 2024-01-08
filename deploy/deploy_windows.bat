@ECHO OFF
cd ..
set /p Version=<deploy/version.txt
echo Preparing version %Version%

:start
SET choice=
SET /p choice=Create exe for interface_creator [Y]: 
IF NOT '%choice%'=='' SET choice=%choice:~0,1%
IF '%choice%'=='Y' GOTO create_interface_creator_exe
IF '%choice%'=='y' GOTO create_interface_creator_exe
IF '%choice%'=='N' GOTO continue
IF '%choice%'=='n' GOTO continue
IF '%choice%'=='' GOTO create_interface_creator_exe
ECHO "%choice%" is not valid
ECHO.
GOTO start

:create_interface_creator_exe
echo Build interface_creator.exe
cd interface_creator/python && python setup.py build
cd ../..

:continue
echo Packing VND_v%Version%.zip
7z a -tzip ../VND_v%Version%.zip -xr!.git -xr!deploy.bat -xr!env ../VND
rem 7z a -sfx7z.sfx ../VND_v%Version%.exe -xr!.git -xr!deploy.bat -xr!env ../VND