@echo off
REM Windows batch file to open WSL in Compass directory
echo ====================================
echo   Compass - Open in WSL
echo ====================================
echo.
echo Opening WSL in /home/wsl-user/compass...
echo.

wsl -d Ubuntu-24.04-Anthropic --cd /home/wsl-user/compass

