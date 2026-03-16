@echo off
if not defined in_subprocess (cmd /k set in_subprocess=y ^& %0 %*) & exit /b

setlocal enabledelayedexpansion

call cls

cd /d %~dp0
set dist_dir=!CD!\dist
if exist "!dist_dir!" rmdir "!dist_dir!" /s /q >nul 2>&1
if exist "!CD!\build" rmdir "!CD!\build" /s /q >nul 2>&1
mkdir "!dist_dir!"

echo ======================================================================
echo    Building distributable application
echo ======================================================================

set "LION_ENV_NAME=.venv"
set "python_exe=!LION_ENV_NAME!\Scripts\python.exe"

call !LION_ENV_NAME!\Scripts\activate.bat
if !errorlevel! neq 0 (
    echo Failed to activate virtual environment. Exiting ...
    goto exiting
)

call !python_exe! -m pip install --upgrade pip setuptools wheel
if !ERRORLEVEL! neq 0 echo Failed to upgrade pip, setuptools, or wheel.

echo Installing build module if not already installed ...
call !python_exe! -m pip install --upgrade build
if !ERRORLEVEL! neq 0 (
    echo Failed to install build module. Exiting ...
    goto exiting
)

if exist !dist_dir! (
    rmdir /s /q !dist_dir!
    if !ERRORLEVEL! neq 0 (
        echo Failed to remove existing dist directory.
    )
)

echo building the distributable packages, *.tar.gz and *.whl files ... please wait ...
@REM --wheel → builds only .whl
@REM --sdist → builds only .tar.gz
call !python_exe! -m build --wheel
if !ERRORLEVEL! neq 0 (
    echo Build process failed. Please check the output for details.
    echo Build process failed. Please check the output for details. > build.log
)

echo Build process completed. Moving to onboarding assets directory ...
if not exist !dist_dir! (
    mkdir !dist_dir!
    if !ERRORLEVEL! neq 0 (
        echo Failed to create assets directory in onboarding.
        goto exiting
    )
)

echo Copying distributable packages to onboarding assets directory ...
if not exist !dist_dir!\* (
    echo No files found in dist directory. Exiting ...
    goto exiting
)

move /Y !dist_dir!\* !dist_dir!
if !ERRORLEVEL!==0 (
    rmdir /s /q !dist_dir!
    if !ERRORLEVEL! neq 0 (
        echo Failed to remove dist directory after moving files.
    )
)

if exist !CD!\build (
    rmdir /s /q !CD!\build
    if !ERRORLEVEL! neq 0 (
        echo Failed to remove build directory after build process.
    )
)

if exist !CD!\build.log (
    del /q !CD!\build.log
    if !ERRORLEVEL! neq 0 (
        echo Failed to delete build log file.
    )
)

endlocal
