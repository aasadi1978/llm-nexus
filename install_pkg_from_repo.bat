@echo off
setlocal enabledelayedexpansion

::-----------------------------------------------------------------------------
:: Script to install LION package from GitHub repository using pip and a virtual environment.
set "app=llm-nexus"
set "project_home=!CD!"
set "venv_path=!project_home!\.venv"
SET "repo_url=github.com/alireza-asadi_fedex"
::-----------------------------------------------------------------------------

rem --- Check if Git is installed, install if not ---
echo [!date! !time!] Checking if Git is installed...
where git >NUL 2>&1
if !errorlevel! neq 0 (
    echo [!date! !time!] Git not found. Installing Git silently...
    set "git_installer=git_executable.exe"
    if not exist "!git_installer!" (
        echo [!date! !time!] Git installer not found at !git_installer!.
        pause
        goto exit_update
    )
    "!git_installer!" /VERYSILENT /NORESTART /NOCANCEL /SP- /CLOSEAPPLICATIONS /RESTARTAPPLICATIONS /COMPONENTS="icons,ext\reg\shellhere,assoc,assoc_sh"
    if !errorlevel! neq 0 (
        echo [!date! !time!] Git installation failed with error code !errorlevel!.
        goto exit_update
    )
    rem Refresh PATH so git is available in this session
    set "PATH=%PATH%;C:\Program Files\Git\cmd"
    echo [!date! !time!] Git installed successfully.
) else (
    echo [!date! !time!] Git is already installed.
)

if not defined ALL_REPO_READ_ONLY_TOKEN (
    echo [!date! !time!] ALL_REPO_READ_ONLY_TOKEN environment variable is not set.
    :: prompt user to set the token
    set /p "token_key=Please enter your ALL_REPO_READ_ONLY_TOKEN:"
    if not defined token_key (
        echo [!date! !time!] No token entered. Exiting update process.
        pause
        goto exit_update
    )
    SET "token_key=!token_key!"
    SETX ALL_REPO_READ_ONLY_TOKEN !token_key! >nul
    echo [!date! !time!] ALL_REPO_READ_ONLY_TOKEN environment variable set successfully to !token_key!.

) else (
    SET "token_key=!ALL_REPO_READ_ONLY_TOKEN!"
)

echo Building GitHub URL with token for repository access...
set "github_url=git+https://x-access-token:!token_key!@!repo_url!/!app!.git"

if not exist "!venv_path!\Scripts" (
    call python -m venv "!venv_path!"
    if !errorlevel! neq 0 (
        echo Virtual environment creation failed with error code !errorlevel!. Please check your Python installation and permissions.
        pause
        goto exit_update
    )
    echo Virtual environment created successfully at !venv_path!.
)

echo Activating virtual environment at !venv_path!...
call "!venv_path!\Scripts\activate.bat"
if !errorlevel! neq 0 (
    echo Failed to activate virtual environment with error code !errorlevel!. Please check the virtual environment setup.
    pause
    goto exit_update
)

rem --- Setup project directory ---
echo [!date! !time!] Installing package !app! ...  
echo [!date! !time!] Installing !app! package... 
!venv_path!\Scripts\python.exe -m pip install !github_url!
if !errorlevel! neq 0 (
    echo [!date! !time!] Installation of !github_url! failed with error code !ERRORLEVEL!. 
)

:: replace - by _ in app name for import
set "import_app=!app:-=_!"

echo validate installation of !app! package...
!venv_path!\Scripts\python.exe -c "import !import_app!; print('!app! package imported successfully. Version:', !import_app__.__version__)"
if !errorlevel! neq 0 (
    echo [!date! !time!] Validation of !app! package failed with error code !ERRORLEVEL!. Please check the installation and package integrity.
) else (
    echo [!date! !time!] !app! package installed and validated successfully.
)

echo ------------------------------------------------------------
echo [!date! !time!] Update process completed.  

:exit_update
echo [!date! !time!] Exiting update check. 
endlocal