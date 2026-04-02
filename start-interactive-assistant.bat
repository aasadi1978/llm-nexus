@echo off
setlocal

cd /d "%~dp0"

echo ============================================================
echo Activating virtual environment...
echo ============================================================
call ".venv\Scripts\activate"
if errorlevel 1 (
    echo Failed to activate .venv
    exit /b 1
)

cls

echo.
echo ============================================================
echo Starting InteractiveAssistant chat...
echo ============================================================
python -c "from llm_nexus.assistant import ASSISTANT; ASSISTANT.run_interactive()"
if errorlevel 1 (
    echo.
    echo Interactive assistant exited with an error.
    exit /b 1
)

endlocal
exit /b 0
