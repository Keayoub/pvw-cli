@echo off
REM Celery Worker Management Script for Windows
REM Provides easy management of Celery workers on Windows systems

setlocal enabledelayedexpansion

set SCRIPT_DIR=%~dp0
set BACKEND_DIR=%SCRIPT_DIR%..\backend
set LOG_DIR=%SCRIPT_DIR%..\logs\celery
set PID_DIR=%SCRIPT_DIR%..\pids

REM Create directories if they don't exist
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
if not exist "%PID_DIR%" mkdir "%PID_DIR%"

REM Set Python path
set PYTHONPATH=%BACKEND_DIR%;%PYTHONPATH%

REM Worker configurations
set WORKERS[0]=file_processing_worker:file_processing,high_priority:4
set WORKERS[1]=data_operations_worker:data_operations,analytics:2
set WORKERS[2]=maintenance_worker:maintenance,low_priority:1
set WORKERS[3]=bulk_operations_worker:bulk_operations:6

if "%1"=="" goto :show_usage
if "%1"=="start" goto :start_workers
if "%1"=="stop" goto :stop_workers
if "%1"=="restart" goto :restart_workers
if "%1"=="status" goto :show_status
if "%1"=="monitor" goto :monitor_workers
goto :show_usage

:show_usage
echo Usage: %0 [start^|stop^|restart^|status^|monitor] [worker_name]
echo.
echo Available workers:
echo   - file_processing_worker (queues: file_processing, high_priority)
echo   - data_operations_worker (queues: data_operations, analytics)
echo   - maintenance_worker (queues: maintenance, low_priority)
echo   - bulk_operations_worker (queues: bulk_operations)
echo.
echo Examples:
echo   %0 start                    Start all workers
echo   %0 start file_processing_worker  Start specific worker
echo   %0 stop                     Stop all workers
echo   %0 status                   Show worker status
goto :end

:start_workers
if not "%2"=="" (
    call :start_single_worker %2
) else (
    echo Starting all Celery workers...
    for /L %%i in (0,1,3) do (
        call :parse_worker_config %%i
        call :start_single_worker !WORKER_NAME!
    )
)
goto :end

:start_single_worker
set WORKER_NAME=%1
echo Starting worker: %WORKER_NAME%

REM Find worker configuration
set FOUND=0
for /L %%i in (0,1,3) do (
    call :parse_worker_config %%i
    if "!WORKER_NAME!"=="!WORKER_CONFIG_NAME!" (
        set FOUND=1
        goto :start_worker_found
    )
)

if %FOUND%==0 (
    echo Error: Worker %WORKER_NAME% not found
    goto :end
)

:start_worker_found
set LOG_FILE=%LOG_DIR%\%WORKER_NAME%.log
set PID_FILE=%PID_DIR%\%WORKER_NAME%.pid

REM Check if worker is already running
if exist "%PID_FILE%" (
    set /p EXISTING_PID=<"%PID_FILE%"
    tasklist /FI "PID eq !EXISTING_PID!" 2>NUL | find /I "python" >NUL
    if !ERRORLEVEL!==0 (
        echo Worker %WORKER_NAME% is already running with PID !EXISTING_PID!
        goto :end
    ) else (
        echo Cleaning up stale PID file for %WORKER_NAME%
        del "%PID_FILE%" 2>NUL
    )
)

REM Build celery command
set CELERY_CMD=celery -A app.core.celery_app:celery_app worker
set CELERY_CMD=%CELERY_CMD% --hostname=%WORKER_NAME%@%%h
set CELERY_CMD=%CELERY_CMD% --concurrency=%WORKER_CONCURRENCY%
set CELERY_CMD=%CELERY_CMD% --queues=%WORKER_QUEUES%
set CELERY_CMD=%CELERY_CMD% --loglevel=INFO
set CELERY_CMD=%CELERY_CMD% --prefetch-multiplier=1
set CELERY_CMD=%CELERY_CMD% --max-memory-per-child=200000
set CELERY_CMD=%CELERY_CMD% --logfile="%LOG_FILE%"

REM Start worker in background and capture PID
echo Starting: %CELERY_CMD%
cd /d "%BACKEND_DIR%"
start /B "Celery_%WORKER_NAME%" cmd /c "%CELERY_CMD%" ^& echo %%^! ^> "%PID_FILE%"

REM Wait a moment and verify startup
timeout /t 3 /nobreak >NUL
if exist "%PID_FILE%" (
    set /p NEW_PID=<"%PID_FILE%"
    echo Worker %WORKER_NAME% started with PID !NEW_PID!
) else (
    echo Failed to start worker %WORKER_NAME%
)
goto :end

:stop_workers
if not "%2"=="" (
    call :stop_single_worker %2
) else (
    echo Stopping all Celery workers...
    for /L %%i in (0,1,3) do (
        call :parse_worker_config %%i
        call :stop_single_worker !WORKER_NAME!
    )
)
goto :end

:stop_single_worker
set WORKER_NAME=%1
set PID_FILE=%PID_DIR%\%WORKER_NAME%.pid

if not exist "%PID_FILE%" (
    echo Worker %WORKER_NAME% PID file not found
    goto :end
)

set /p WORKER_PID=<"%PID_FILE%"
echo Stopping worker %WORKER_NAME% (PID: %WORKER_PID%)

REM Try graceful shutdown first
taskkill /PID %WORKER_PID% /T 2>NUL
timeout /t 10 /nobreak >NUL

REM Check if process is still running
tasklist /FI "PID eq %WORKER_PID%" 2>NUL | find /I "python" >NUL
if %ERRORLEVEL%==0 (
    echo Forcefully terminating worker %WORKER_NAME%
    taskkill /F /PID %WORKER_PID% /T 2>NUL
)

del "%PID_FILE%" 2>NUL
echo Worker %WORKER_NAME% stopped
goto :end

:restart_workers
echo Restarting workers...
call :stop_workers %2
timeout /t 5 /nobreak >NUL
call :start_workers %2
goto :end

:show_status
echo Celery Worker Status
echo ====================
echo.

for /L %%i in (0,1,3) do (
    call :parse_worker_config %%i
    call :show_worker_status !WORKER_NAME!
)

REM Show Celery inspect information
echo.
echo Celery Inspect Information:
echo ---------------------------
cd /d "%BACKEND_DIR%"
celery -A app.core.celery_app:celery_app inspect active 2>NUL
goto :end

:show_worker_status
set WORKER_NAME=%1
set PID_FILE=%PID_DIR%\%WORKER_NAME%.pid

echo Worker: %WORKER_NAME%
if exist "%PID_FILE%" (
    set /p WORKER_PID=<"%PID_FILE%"
    tasklist /FI "PID eq !WORKER_PID!" 2>NUL | find /I "python" >NUL
    if !ERRORLEVEL!==0 (
        echo   Status: RUNNING
        echo   PID: !WORKER_PID!
        
        REM Get memory usage
        for /f "tokens=5" %%a in ('tasklist /FI "PID eq !WORKER_PID!" /FO CSV ^| find "python"') do (
            set MEM_USAGE=%%a
            set MEM_USAGE=!MEM_USAGE:"=!
            echo   Memory: !MEM_USAGE!
        )
    ) else (
        echo   Status: STOPPED (stale PID file)
        del "%PID_FILE%" 2>NUL
    )
) else (
    echo   Status: NOT RUNNING
)
echo.
goto :end

:monitor_workers
echo Starting worker monitoring (Press Ctrl+C to stop)...
:monitor_loop
cls
call :show_status
timeout /t 30 /nobreak >NUL
goto :monitor_loop

:parse_worker_config
set INDEX=%1
set CONFIG=!WORKERS[%INDEX%]!
for /f "tokens=1,2,3 delims=:" %%a in ("!CONFIG!") do (
    set WORKER_CONFIG_NAME=%%a
    set WORKER_QUEUES=%%b
    set WORKER_CONCURRENCY=%%c
)
set WORKER_NAME=!WORKER_CONFIG_NAME!
goto :end

:end
endlocal
