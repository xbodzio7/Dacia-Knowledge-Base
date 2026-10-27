@echo off
echo.
echo ===== Wysylanie zmian do GitHub =====

git status --porcelain >nul

for /f %%i in ('git status --porcelain') do goto :continue

echo Brak zmian do wyslania.
pause
exit /b

:continue
git add .

set /p msg=Podaj opis zmian: 

git commit -m "%msg%"
git push

pause