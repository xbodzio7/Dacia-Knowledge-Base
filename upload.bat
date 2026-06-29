@echo off
echo.
echo ===== Wysylanie zmian do GitHub =====
git add .
set /p msg=Podaj opis zmian: 
git commit -m "%msg%"
git push
pause