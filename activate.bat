@echo off

echo ======================================================================
echo    Activating any existing virtual environment ...
echo ======================================================================

call cls
call .venv\Scripts\activate
if errorlevel 1 (
    echo Failed to activate virtual environment!
    exit /b 1
)
echo Virtual environment activated successfully.
exit /b 0