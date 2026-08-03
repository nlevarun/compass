@echo off
REM Windows batch file to push Compass to GitHub from WSL
echo ====================================
echo   Compass - Push to GitHub
echo ====================================
echo.

echo Entering WSL and pushing to GitHub...
echo.

wsl -e bash -c "cd /home/wsl-user/compass && git push -u origin main"

echo.
echo Done!
pause
