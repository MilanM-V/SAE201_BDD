@echo off
echo =======================================================
echo    Mise à jour du projet depuis le repertoire Git
echo =======================================================
echo.

:: Récupération des dernières modifications depuis la branche Milan (ou main)
git pull origin Milan

echo.
echo =======================================================
echo               Mise à jour terminee !
echo =======================================================
pause
