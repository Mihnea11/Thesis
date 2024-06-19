@echo off
cd /d "%~dp0"

echo Starting Mini O Client...
start cmd /k "cd MiniO && minio.exe server --address :9500 "./MiniO Storage""

echo Starting Python FastAPI backend...
start cmd /k "cd ModelOPS && python server.py"

echo Starting Angular frontend...
start cmd /k "cd Frontend && ng serve"

echo All services started.
pause
