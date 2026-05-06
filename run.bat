@echo off
title Sistema de Integracao Facilita
cls

echo ============================================================
echo         INICIALIZADOR DO SISTEMA DE INTEGRACAO
echo ============================================================
echo.

:: Tenta ativar o ambiente virtual se ele existir
if exist ".venv\Scripts\activate.bat" (
    echo [INFO] Ativando ambiente virtual...
    call ".venv\Scripts\activate.bat"
) else (
    echo [AVISO] Ambiente virtual nao encontrado. Rodando no ambiente global.
)

echo.
echo [INFO] Verificando e instalando dependencias...
pip install -r requirements.txt

echo.
echo [INFO] Iniciando o Menu Interativo...
timeout /t 2 >nul

python menu.py

pause
