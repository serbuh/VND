
set /p Version=<version/version.txt
ECHO Packing version %Version%
7z a -sfx7z.sfx ../VND_v%Version%.exe -xr!.git -xr!deploy.bat -xr!env ../VND