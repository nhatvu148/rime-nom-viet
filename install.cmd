@echo off
echo ========================================
echo   Installing Nom Viet for RIME/Weasel
echo ========================================
echo.

set RIME_DIR=%APPDATA%\Rime

if not exist "%RIME_DIR%" (
    echo ERROR: Rime folder not found at %RIME_DIR%
    echo Please install Weasel first: https://github.com/rime/weasel/releases
    pause
    exit /b 1
)

echo Downloading nom_viet.schema.yaml...
curl -L -o "%RIME_DIR%\nom_viet.schema.yaml" https://github.com/nhatvu148/rime-nom-viet/raw/main/nom_viet.schema.yaml

echo Downloading nom_viet.dict.yaml...
curl -L -o "%RIME_DIR%\nom_viet.dict.yaml" https://github.com/nhatvu148/rime-nom-viet/raw/main/nom_viet.dict.yaml

echo.
echo Creating default.custom.yaml...
(
echo patch:
echo   schema_list:
echo     - schema: nom_viet
echo     - schema: luna_pinyin
) > "%RIME_DIR%\default.custom.yaml"

echo.
echo ========================================
echo   Installation complete!
echo ========================================
echo.
echo Files installed to: %RIME_DIR%
echo.
echo NEXT STEPS:
echo   1. Right-click Weasel icon in system tray
echo   2. Click "重新部署" (Deploy)
echo   3. Press Ctrl+` or F4 to select "Nom Viet"
echo.
pause
