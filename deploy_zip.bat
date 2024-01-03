
set /p Version=<version/version.txt
ECHO Packing version %Version%
7z a -tzip ../VND_v%Version%.zip -xr!.git -xr!deploy.bat -xr!env ../VND